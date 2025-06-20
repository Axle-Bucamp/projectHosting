# Backend Service
resource "google_compute_backend_service" "app_backend" {
  name                  = "startup-backend-service"
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL"
  timeout_sec           = 30
  enable_cdn            = true

  backend {
    group           = google_compute_region_instance_group_manager.app_group.instance_group
    balancing_mode  = "UTILIZATION"
    capacity_scaler = 1.0
  }

  health_checks = [google_compute_health_check.app_health_check.id]

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
resource "google_compute_url_map" "app_url_map" {
  name            = "startup-url-map"
  default_service = google_compute_backend_service.app_backend.id

  host_rule {
    hosts        = [var.domain_name, "www.${var.domain_name}"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.app_backend.id

    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.app_backend.id
    }

    path_rule {
      paths   = ["/*"]
      service = google_compute_backend_service.app_backend.id
    }
  }
}

# SSL Certificate
resource "google_compute_managed_ssl_certificate" "app_ssl_cert" {
  name = var.ssl_certificate_name

  managed {
    domains = [var.domain_name, "www.${var.domain_name}"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

# HTTPS Proxy
resource "google_compute_target_https_proxy" "app_https_proxy" {
  name             = "startup-https-proxy"
  url_map          = google_compute_url_map.app_url_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.app_ssl_cert.id]
}

# HTTP Proxy (for redirect)
resource "google_compute_target_http_proxy" "app_http_proxy" {
  name    = "startup-http-proxy"
  url_map = google_compute_url_map.redirect_url_map.id
}

# URL Map for HTTP to HTTPS redirect
resource "google_compute_url_map" "redirect_url_map" {
  name = "startup-redirect-url-map"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

# Global Forwarding Rule for HTTPS
resource "google_compute_global_forwarding_rule" "app_https_forwarding_rule" {
  name                  = "startup-https-forwarding-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "443"
  target                = google_compute_target_https_proxy.app_https_proxy.id
  ip_address            = google_compute_global_address.app_ip.id
}

# Global Forwarding Rule for HTTP
resource "google_compute_global_forwarding_rule" "app_http_forwarding_rule" {
  name                  = "startup-http-forwarding-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "80"
  target                = google_compute_target_http_proxy.app_http_proxy.id
  ip_address            = google_compute_global_address.app_ip.id
}

