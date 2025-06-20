# Outputs
output "load_balancer_ip" {
  description = "IP address of the load balancer"
  value       = google_compute_global_forwarding_rule.app_forwarding_rule.ip_address
}

output "load_balancer_https_ip" {
  description = "IP address of the HTTPS load balancer"
  value       = google_compute_global_forwarding_rule.app_https_forwarding_rule.ip_address
}

output "dns_name_servers" {
  description = "Name servers for the DNS zone"
  value       = google_dns_managed_zone.startup_zone.name_servers
}

output "database_connection_name" {
  description = "Connection name for Cloud SQL instance"
  value       = google_sql_database_instance.postgres.connection_name
}

output "database_private_ip" {
  description = "Private IP address of the database"
  value       = google_sql_database_instance.postgres.private_ip_address
  sensitive   = true
}

output "static_bucket_name" {
  description = "Name of the static assets bucket"
  value       = google_storage_bucket.static_assets.name
}

output "static_bucket_url" {
  description = "URL of the static assets bucket"
  value       = google_storage_bucket.static_assets.url
}

output "vpc_network_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.startup_vpc.name
}

output "app_subnet_name" {
  description = "Name of the application subnet"
  value       = google_compute_subnetwork.app_subnet.name
}

output "admin_subnet_name" {
  description = "Name of the admin subnet"
  value       = google_compute_subnetwork.admin_subnet.name
}

output "app_service_account_email" {
  description = "Email of the application service account"
  value       = google_service_account.app_service_account.email
}

output "admin_service_account_email" {
  description = "Email of the admin service account"
  value       = google_service_account.admin_service_account.email
}

output "tailscale_auth_key" {
  description = "Tailscale auth key for device registration"
  value       = tailscale_tailnet_key.admin_key.key
  sensitive   = true
}

output "ssl_certificate_status" {
  description = "Status of the SSL certificate"
  value       = google_compute_managed_ssl_certificate.app_ssl_cert.managed[0].status
}

output "app_instance_group_manager" {
  description = "Name of the app instance group manager"
  value       = google_compute_region_instance_group_manager.app_group.name
}

output "admin_instance_group_manager" {
  description = "Name of the admin instance group manager"
  value       = google_compute_instance_group_manager.admin_group.name
}

# Connection information for applications
output "connection_info" {
  description = "Connection information for applications"
  value = {
    frontend_url    = "https://${var.domain_name}"
    api_url         = "https://${var.domain_name}/api"
    admin_url       = "Available via Tailscale network"
    monitoring_url  = "Available via Tailscale network"
    database_host   = google_sql_database_instance.postgres.private_ip_address
    database_name   = google_sql_database.startup_db.name
    static_assets   = google_storage_bucket.static_assets.url
  }
  sensitive = true
}

# Deployment commands
output "deployment_commands" {
  description = "Commands for deployment and management"
  value = {
    build_images = [
      "docker build -t gcr.io/${var.project_id}/frontend:latest ./services/frontend",
      "docker build -t gcr.io/${var.project_id}/backend:latest ./backend-api",
      "docker build -t gcr.io/${var.project_id}/admin:latest ./admin-interface"
    ]
    push_images = [
      "docker push gcr.io/${var.project_id}/frontend:latest",
      "docker push gcr.io/${var.project_id}/backend:latest",
      "docker push gcr.io/${var.project_id}/admin:latest"
    ]
    update_instances = [
      "gcloud compute instance-groups managed rolling-action start-update ${google_compute_region_instance_group_manager.app_group.name} --version template=${google_compute_instance_template.app_template.name} --region=${var.region}",
      "gcloud compute instance-groups managed rolling-action start-update ${google_compute_instance_group_manager.admin_group.name} --version template=${google_compute_instance_template.admin_template.name} --zone=${var.zone}"
    ]
  }
}

# Monitoring endpoints
output "monitoring_endpoints" {
  description = "Monitoring and admin endpoints (Tailscale access required)"
  value = {
    grafana     = "http://admin.startup.local:3001"
    prometheus  = "http://admin.startup.local:9090"
    admin_panel = "http://admin.startup.local:8080"
  }
}

