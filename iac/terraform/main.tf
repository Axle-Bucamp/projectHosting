# Enhanced Terraform Configuration for Production
# Startup Website Infrastructure with Advanced Monitoring

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
  
  backend "gcs" {
    bucket = var.terraform_state_bucket
    prefix = "terraform/state"
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Random password for Redis
resource "random_password" "redis_password" {
  length  = 32
  special = false
}

# Random JWT secret
resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "sql.googleapis.com",
    "redis.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com",
    "dns.googleapis.com",
    "certificatemanager.googleapis.com",
    "storage.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_dependent_services = true
}

# VPC Network
resource "google_compute_network" "startup_vpc" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
  mtu                     = 1460

  depends_on = [google_project_service.required_apis]
}

# Subnet for application
resource "google_compute_subnetwork" "startup_subnet" {
  name          = "${var.project_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.startup_vpc.id

  secondary_ip_range {
    range_name    = "services-range"
    ip_cidr_range = "192.168.1.0/24"
  }

  secondary_ip_range {
    range_name    = "pod-ranges"
    ip_cidr_range = "192.168.64.0/22"
  }
}

# Firewall rules
resource "google_compute_firewall" "allow_http_https" {
  name    = "${var.project_name}-allow-http-https"
  network = google_compute_network.startup_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}

resource "google_compute_firewall" "allow_ssh" {
  name    = "${var.project_name}-allow-ssh"
  network = google_compute_network.startup_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh-server"]
}

resource "google_compute_firewall" "allow_internal" {
  name    = "${var.project_name}-allow-internal"
  network = google_compute_network.startup_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/24", "192.168.1.0/24", "192.168.64.0/22"]
}

resource "google_compute_firewall" "allow_monitoring" {
  name    = "${var.project_name}-allow-monitoring"
  network = google_compute_network.startup_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["9090", "9093", "9100", "3000", "3100", "8080"]
  }

  source_ranges = ["10.0.0.0/24"]
  target_tags   = ["monitoring"]
}

resource "google_compute_firewall" "allow_tailscale" {
  name    = "${var.project_name}-allow-tailscale"
  network = google_compute_network.startup_vpc.name

  allow {
    protocol = "udp"
    ports    = ["41641"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["tailscale"]
}

# Cloud SQL Instance
resource "google_sql_database_instance" "startup_db" {
  name             = "${var.project_name}-db-${random_id.db_name_suffix.hex}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier                        = var.db_tier
    availability_type           = "REGIONAL"
    disk_type                   = "PD_SSD"
    disk_size                   = 20
    disk_autoresize             = true
    disk_autoresize_limit       = 100
    deletion_protection_enabled = var.enable_deletion_protection

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      location                       = var.region
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.startup_vpc.id
      require_ssl     = true
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_disconnections"
      value = "on"
    }

    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }

    maintenance_window {
      day          = 7
      hour         = 3
      update_track = "stable"
    }
  }

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

# Database
resource "google_sql_database" "startup_database" {
  name     = "startup_db"
  instance = google_sql_database_instance.startup_db.name
}

# Database user
resource "google_sql_user" "startup_user" {
  name     = "startup"
  instance = google_sql_database_instance.startup_db.name
  password = random_password.db_password.result
}

# Private service connection for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.project_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.startup_vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.startup_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# Redis Instance
resource "google_redis_instance" "startup_cache" {
  name           = "${var.project_name}-cache"
  tier           = "STANDARD_HA"
  memory_size_gb = 1
  region         = var.region

  location_id             = var.zone
  alternative_location_id = "${substr(var.region, 0, length(var.region)-2)}-b"

  authorized_network = google_compute_network.startup_vpc.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  redis_version     = "REDIS_7_0"
  display_name      = "Startup Cache"
  reserved_ip_range = "192.168.0.0/29"

  auth_enabled = true
}

# Secret Manager for sensitive data
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${var.project_name}-db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret" "redis_auth" {
  secret_id = "${var.project_name}-redis-auth"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "redis_auth" {
  secret      = google_secret_manager_secret.redis_auth.id
  secret_data = google_redis_instance.startup_cache.auth_string
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "${var.project_name}-jwt-secret"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = random_password.jwt_secret.result
}

resource "google_secret_manager_secret" "tailscale_auth_key" {
  secret_id = "${var.project_name}-tailscale-auth-key"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "tailscale_auth_key" {
  secret      = google_secret_manager_secret.tailscale_auth_key.id
  secret_data = var.tailscale_auth_key
}

# Service Account for instances
resource "google_service_account" "startup_sa" {
  account_id   = "${var.project_name}-sa"
  display_name = "Startup Service Account"
  description  = "Service account for startup website instances"
}

resource "google_project_iam_member" "startup_sa_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.dashboardEditor",
    "roles/secretmanager.secretAccessor",
    "roles/cloudsql.client",
    "roles/redis.editor",
    "roles/storage.objectViewer"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.startup_sa.email}"
}

# Instance Template for Application Servers
resource "google_compute_instance_template" "startup_template" {
  name_prefix  = "${var.project_name}-template-"
  machine_type = var.machine_type
  region       = var.region

  tags = ["web-server", "ssh-server", "monitoring", "tailscale"]

  disk {
    source_image = "cos-cloud/cos-stable"
    auto_delete  = true
    boot         = true
    disk_size_gb = 20
    disk_type    = "pd-ssd"
  }

  network_interface {
    network    = google_compute_network.startup_vpc.id
    subnetwork = google_compute_subnetwork.startup_subnet.id

    access_config {
      network_tier = "PREMIUM"
    }
  }

  service_account {
    email  = google_service_account.startup_sa.email
    scopes = ["cloud-platform"]
  }

  metadata = {
    "gce-container-declaration" = file("${path.module}/container-declaration.yaml")
    "google-logging-enabled"    = "true"
    "google-monitoring-enabled" = "true"
    "startup-script"           = templatefile("${path.module}/startup-script.sh", {
      project_id         = var.project_id
      db_connection_name = google_sql_database_instance.startup_db.connection_name
      redis_host         = google_redis_instance.startup_cache.host
      redis_port         = google_redis_instance.startup_cache.port
    })
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Instance Template for Admin Servers (Tailscale)
resource "google_compute_instance_template" "admin_template" {
  name_prefix  = "${var.project_name}-admin-template-"
  machine_type = "e2-micro"
  region       = var.region

  tags = ["ssh-server", "monitoring", "tailscale", "admin"]

  disk {
    source_image = "cos-cloud/cos-stable"
    auto_delete  = true
    boot         = true
    disk_size_gb = 10
    disk_type    = "pd-standard"
  }

  network_interface {
    network    = google_compute_network.startup_vpc.id
    subnetwork = google_compute_subnetwork.startup_subnet.id
  }

  service_account {
    email  = google_service_account.startup_sa.email
    scopes = ["cloud-platform"]
  }

  metadata = {
    "gce-container-declaration" = file("${path.module}/admin-container-declaration.yaml")
    "google-logging-enabled"    = "true"
    "google-monitoring-enabled" = "true"
    "startup-script"           = templatefile("${path.module}/admin-startup-script.sh", {
      project_id         = var.project_id
      tailscale_auth_key = var.tailscale_auth_key
    })
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Health Check
resource "google_compute_health_check" "startup_health_check" {
  name                = "${var.project_name}-health-check"
  check_interval_sec  = 30
  timeout_sec         = 10
  healthy_threshold   = 2
  unhealthy_threshold = 3

  http_health_check {
    port         = 80
    request_path = "/api/health"
  }
}

# Managed Instance Group for Application
resource "google_compute_region_instance_group_manager" "startup_mig" {
  name   = "${var.project_name}-mig"
  region = var.region

  base_instance_name = "${var.project_name}-instance"
  target_size        = var.min_instances

  version {
    instance_template = google_compute_instance_template.startup_template.id
  }

  named_port {
    name = "http"
    port = 80
  }

  named_port {
    name = "https"
    port = 443
  }

  auto_healing_policies {
    health_check      = google_compute_health_check.startup_health_check.id
    initial_delay_sec = 300
  }

  update_policy {
    type                         = "PROACTIVE"
    instance_redistribution_type = "PROACTIVE"
    minimal_action               = "REPLACE"
    max_surge_fixed              = 2
    max_unavailable_fixed        = 1
  }
}

# Auto Scaler
resource "google_compute_region_autoscaler" "startup_autoscaler" {
  name   = "${var.project_name}-autoscaler"
  region = var.region
  target = google_compute_region_instance_group_manager.startup_mig.id

  autoscaling_policy {
    max_replicas    = var.max_instances
    min_replicas    = var.min_instances
    cooldown_period = 300

    cpu_utilization {
      target = 0.7
    }

    load_balancing_utilization {
      target = 0.8
    }

    metric {
      name   = "compute.googleapis.com/instance/network/received_bytes_count"
      target = 1000
      type   = "GAUGE"
    }
  }
}

# Admin Instance Group (Single instance)
resource "google_compute_region_instance_group_manager" "admin_mig" {
  name   = "${var.project_name}-admin-mig"
  region = var.region

  base_instance_name = "${var.project_name}-admin"
  target_size        = 1

  version {
    instance_template = google_compute_instance_template.admin_template.id
  }

  named_port {
    name = "admin"
    port = 3000
  }
}

# Load Balancer Components
resource "google_compute_global_address" "startup_ip" {
  name = "${var.project_name}-ip"
}

resource "google_compute_backend_service" "startup_backend" {
  name                  = "${var.project_name}-backend"
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL"
  timeout_sec           = 30
  enable_cdn            = true

  backend {
    group           = google_compute_region_instance_group_manager.startup_mig.instance_group
    balancing_mode  = "UTILIZATION"
    capacity_scaler = 1.0
  }

  health_checks = [google_compute_health_check.startup_health_check.id]

  cdn_policy {
    cache_mode                   = "CACHE_ALL_STATIC"
    default_ttl                  = 3600
    max_ttl                      = 86400
    negative_caching             = true
    serve_while_stale            = 86400
    signed_url_cache_max_age_sec = 7200

    cache_key_policy {
      include_host         = true
      include_protocol     = true
      include_query_string = false
    }
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }
}

# URL Map
resource "google_compute_url_map" "startup_url_map" {
  name            = "${var.project_name}-url-map"
  default_service = google_compute_backend_service.startup_backend.id

  host_rule {
    hosts        = [var.domain_name]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.startup_backend.id

    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.startup_backend.id
    }

    path_rule {
      paths   = ["/*"]
      service = google_compute_backend_service.startup_backend.id
    }
  }
}

# SSL Certificate
resource "google_compute_managed_ssl_certificate" "startup_ssl" {
  name = "${var.project_name}-ssl"

  managed {
    domains = [var.domain_name, "www.${var.domain_name}"]
  }
}

# HTTPS Proxy
resource "google_compute_target_https_proxy" "startup_https_proxy" {
  name             = "${var.project_name}-https-proxy"
  url_map          = google_compute_url_map.startup_url_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.startup_ssl.id]
}

# HTTP Proxy (for redirect)
resource "google_compute_target_http_proxy" "startup_http_proxy" {
  name    = "${var.project_name}-http-proxy"
  url_map = google_compute_url_map.startup_redirect.id
}

# URL Map for HTTP to HTTPS redirect
resource "google_compute_url_map" "startup_redirect" {
  name = "${var.project_name}-redirect"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

# Global Forwarding Rules
resource "google_compute_global_forwarding_rule" "startup_https" {
  name       = "${var.project_name}-https-rule"
  target     = google_compute_target_https_proxy.startup_https_proxy.id
  port_range = "443"
  ip_address = google_compute_global_address.startup_ip.address
}

resource "google_compute_global_forwarding_rule" "startup_http" {
  name       = "${var.project_name}-http-rule"
  target     = google_compute_target_http_proxy.startup_http_proxy.id
  port_range = "80"
  ip_address = google_compute_global_address.startup_ip.address
}

# Cloud Storage for static assets
resource "google_storage_bucket" "startup_assets" {
  name          = "${var.project_id}-startup-assets"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = ["https://${var.domain_name}"]
    method          = ["GET", "HEAD"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# Cloud Storage for backups
resource "google_storage_bucket" "startup_backups" {
  name          = "${var.project_id}-startup-backups"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

# Monitoring and Alerting
resource "google_monitoring_alert_policy" "high_cpu" {
  display_name = "High CPU Usage"
  combiner     = "OR"

  conditions {
    display_name = "CPU usage above 80%"

    condition_threshold {
      filter          = "resource.type=\"gce_instance\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.8

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]

  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_alert_policy" "high_memory" {
  display_name = "High Memory Usage"
  combiner     = "OR"

  conditions {
    display_name = "Memory usage above 85%"

    condition_threshold {
      filter          = "resource.type=\"gce_instance\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.85

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
}

resource "google_monitoring_alert_policy" "service_down" {
  display_name = "Service Down"
  combiner     = "OR"

  conditions {
    display_name = "Health check failing"

    condition_threshold {
      filter          = "resource.type=\"gce_instance\""
      duration        = "180s"
      comparison      = "COMPARISON_LESS_THAN"
      threshold_value = 1

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]

  alert_strategy {
    auto_close = "300s"
  }
}

# Notification Channel
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notification"
  type         = "email"

  labels = {
    email_address = var.admin_email
  }
}

# Cloud DNS (if managing DNS)
resource "google_dns_managed_zone" "startup_zone" {
  count       = var.manage_dns ? 1 : 0
  name        = "${var.project_name}-zone"
  dns_name    = "${var.domain_name}."
  description = "DNS zone for ${var.domain_name}"

  dnssec_config {
    state = "on"
  }
}

resource "google_dns_record_set" "startup_a" {
  count        = var.manage_dns ? 1 : 0
  name         = google_dns_managed_zone.startup_zone[0].dns_name
  managed_zone = google_dns_managed_zone.startup_zone[0].name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_address.startup_ip.address]
}

resource "google_dns_record_set" "startup_www" {
  count        = var.manage_dns ? 1 : 0
  name         = "www.${google_dns_managed_zone.startup_zone[0].dns_name}"
  managed_zone = google_dns_managed_zone.startup_zone[0].name
  type         = "CNAME"
  ttl          = 300

  rrdatas = [var.domain_name]
}

