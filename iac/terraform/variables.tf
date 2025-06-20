# Project Configuration
variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_name" {
  description = "Name of the project (used for resource naming)"
  type        = string
  default     = "startup-website"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "The GCP zone"
  type        = string
  default     = "europe-west1-b"
}

# Domain Configuration
variable "domain_name" {
  description = "The domain name for the website"
  type        = string
}

variable "manage_dns" {
  description = "Whether to manage DNS with Cloud DNS"
  type        = bool
  default     = false
}

# Infrastructure Configuration
variable "machine_type" {
  description = "Machine type for compute instances"
  type        = string
  default     = "e2-standard-2"
}

variable "min_instances" {
  description = "Minimum number of instances in the managed instance group"
  type        = number
  default     = 2
}

variable "max_instances" {
  description = "Maximum number of instances in the managed instance group"
  type        = number
  default     = 10
}

variable "db_tier" {
  description = "The tier for the Cloud SQL instance"
  type        = string
  default     = "db-f1-micro"
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for the database"
  type        = bool
  default     = true
}

# Security Configuration
variable "admin_email" {
  description = "Email address for admin notifications"
  type        = string
}

variable "tailscale_auth_key" {
  description = "Tailscale authentication key for admin access"
  type        = string
  sensitive   = true
}

# Monitoring Configuration
variable "slack_webhook_url" {
  description = "Slack webhook URL for notifications"
  type        = string
  default     = ""
  sensitive   = true
}

variable "enable_monitoring" {
  description = "Enable advanced monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable centralized logging"
  type        = bool
  default     = true
}

# Storage Configuration
variable "terraform_state_bucket" {
  description = "GCS bucket for Terraform state"
  type        = string
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
}

# Application Configuration
variable "app_version" {
  description = "Version of the application to deploy"
  type        = string
  default     = "latest"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# Docker Configuration
variable "docker_registry" {
  description = "Docker registry for container images"
  type        = string
  default     = "gcr.io"
}

variable "enable_watchtower" {
  description = "Enable Watchtower for automatic updates"
  type        = bool
  default     = true
}

# Network Configuration
variable "enable_cdn" {
  description = "Enable Cloud CDN"
  type        = bool
  default     = true
}

variable "enable_ssl" {
  description = "Enable SSL/TLS"
  type        = bool
  default     = true
}

# Cost Optimization
variable "enable_preemptible" {
  description = "Use preemptible instances for cost savings"
  type        = bool
  default     = false
}

variable "disk_size_gb" {
  description = "Boot disk size in GB"
  type        = number
  default     = 20
}

# Feature Flags
variable "enable_redis_ha" {
  description = "Enable Redis high availability"
  type        = bool
  default     = true
}

variable "enable_sql_ha" {
  description = "Enable SQL high availability"
  type        = bool
  default     = true
}

variable "enable_auto_scaling" {
  description = "Enable auto scaling"
  type        = bool
  default     = true
}

# Development Configuration
variable "enable_debug" {
  description = "Enable debug mode"
  type        = bool
  default     = false
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR."
  }
}

# Compliance and Security
variable "enable_audit_logs" {
  description = "Enable audit logging"
  type        = bool
  default     = true
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC flow logs"
  type        = bool
  default     = true
}

variable "enable_binary_authorization" {
  description = "Enable binary authorization for containers"
  type        = bool
  default     = false
}

# Backup Configuration
variable "enable_automated_backups" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "backup_schedule" {
  description = "Cron schedule for backups"
  type        = string
  default     = "0 3 * * *"
}

# Maintenance Configuration
variable "maintenance_window_day" {
  description = "Day of week for maintenance (1-7, 1=Monday)"
  type        = number
  default     = 7
}

variable "maintenance_window_hour" {
  description = "Hour of day for maintenance (0-23)"
  type        = number
  default     = 3
}

# Resource Labels
variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    project     = "startup-website"
    environment = "production"
    managed_by  = "terraform"
  }
}

# External Services
variable "external_monitoring_endpoint" {
  description = "External monitoring endpoint URL"
  type        = string
  default     = ""
}

variable "external_logging_endpoint" {
  description = "External logging endpoint URL"
  type        = string
  default     = ""
}

