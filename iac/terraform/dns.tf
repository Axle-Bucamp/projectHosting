# DNS Zone
resource "google_dns_managed_zone" "app_zone" {
  name        = "startup-zone"
  dns_name    = "${var.domain_name}."
  description = "DNS zone for startup website"

  dnssec_config {
    state = "on"
  }

  labels = var.common_tags
}

# A Record for root domain
resource "google_dns_record_set" "app_a_record" {
  name         = google_dns_managed_zone.app_zone.dns_name
  managed_zone = google_dns_managed_zone.app_zone.name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_address.app_ip.address]
}

# A Record for www subdomain
resource "google_dns_record_set" "app_www_a_record" {
  name         = "www.${google_dns_managed_zone.app_zone.dns_name}"
  managed_zone = google_dns_managed_zone.app_zone.name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_address.app_ip.address]
}

# CNAME Record for API subdomain
resource "google_dns_record_set" "api_cname_record" {
  name         = "api.${google_dns_managed_zone.app_zone.dns_name}"
  managed_zone = google_dns_managed_zone.app_zone.name
  type         = "CNAME"
  ttl          = 300

  rrdatas = [var.domain_name]
}

# MX Records for email
resource "google_dns_record_set" "app_mx_record" {
  name         = google_dns_managed_zone.app_zone.dns_name
  managed_zone = google_dns_managed_zone.app_zone.name
  type         = "MX"
  ttl          = 3600

  rrdatas = [
    "1 aspmx.l.google.com.",
    "5 alt1.aspmx.l.google.com.",
    "5 alt2.aspmx.l.google.com.",
    "10 alt3.aspmx.l.google.com.",
    "10 alt4.aspmx.l.google.com."
  ]
}

# TXT Record for domain verification
resource "google_dns_record_set" "app_txt_record" {
  name         = google_dns_managed_zone.app_zone.dns_name
  managed_zone = google_dns_managed_zone.app_zone.name
  type         = "TXT"
  ttl          = 300

  rrdatas = [
    "\"v=spf1 include:_spf.google.com ~all\"",
    "\"google-site-verification=your-verification-code\""
  ]
}

