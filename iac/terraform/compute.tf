# Instance Template
resource "google_compute_instance_template" "app_template" {
  name_prefix  = "startup-template-"
  machine_type = var.machine_type
  region       = var.region

  disk {
    source_image = "ubuntu-os-cloud/ubuntu-2204-lts"
    auto_delete  = true
    boot         = true
    disk_size_gb = var.disk_size
    disk_type    = "pd-standard"
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.subnet.id

    access_config {
      # Ephemeral public IP
    }
  }

  metadata = {
    ssh-keys = "ubuntu:${file("~/.ssh/id_rsa.pub")}"
  }

  metadata_startup_script = file("${path.module}/startup-script.sh")

  tags = ["http-server", "https-server", "ssh-server"]

  labels = var.common_tags

  lifecycle {
    create_before_destroy = true
  }
}

# Managed Instance Group
resource "google_compute_region_instance_group_manager" "app_group" {
  name   = "startup-instance-group"
  region = var.region

  base_instance_name = "startup-app"
  target_size        = var.instance_count

  version {
    instance_template = google_compute_instance_template.app_template.id
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
    health_check      = google_compute_health_check.app_health_check.id
    initial_delay_sec = 300
  }

  update_policy {
    type                         = "PROACTIVE"
    instance_redistribution_type = "PROACTIVE"
    minimal_action               = "REPLACE"
    max_surge_fixed              = 1
    max_unavailable_fixed        = 0
  }
}

# Health Check
resource "google_compute_health_check" "app_health_check" {
  name               = "startup-health-check"
  check_interval_sec = 30
  timeout_sec        = 10
  healthy_threshold  = 2
  unhealthy_threshold = 3

  http_health_check {
    port         = 80
    request_path = "/api/health"
  }
}

# Autoscaler
resource "google_compute_region_autoscaler" "app_autoscaler" {
  name   = "startup-autoscaler"
  region = var.region
  target = google_compute_region_instance_group_manager.app_group.id

  autoscaling_policy {
    max_replicas    = 5
    min_replicas    = 2
    cooldown_period = 60

    cpu_utilization {
      target = 0.7
    }

    load_balancing_utilization {
      target = 0.8
    }
  }
}

# Static IP for Load Balancer
resource "google_compute_global_address" "app_ip" {
  name         = "startup-lb-ip"
  address_type = "EXTERNAL"
  description  = "Static IP for startup website load balancer"
}

