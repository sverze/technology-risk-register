output "cloud_run_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_service.app.status[0].url
}

output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "The GCP region"
  value       = var.region
}

output "database_bucket_name" {
  description = "The name of the Cloud Storage bucket for database"
  value       = google_storage_bucket.database_bucket.name
}

output "assets_bucket_name" {
  description = "The name of the Cloud Storage bucket for assets"
  value       = google_storage_bucket.assets_bucket.name
}

output "container_registry" {
  description = "The container registry URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.container_repo.repository_id}"
}

output "service_account_email" {
  description = "The email of the Cloud Run service account"
  value       = google_service_account.cloud_run_sa.email
}

output "domain_mapping_status" {
  description = "The status of the domain mapping (if configured)"
  value       = var.domain_name != "" ? google_cloud_run_domain_mapping.domain[0].status : null
}

output "frontend_url" {
  description = "The URL of the frontend (Load Balancer)"
  value       = var.domain_name != "" ? "https://${google_compute_global_forwarding_rule.frontend_https[0].ip_address}" : "http://${google_compute_global_forwarding_rule.frontend_http.ip_address}"
}

output "frontend_ip" {
  description = "The IP address of the frontend load balancer"
  value       = var.domain_name != "" ? google_compute_global_forwarding_rule.frontend_https[0].ip_address : google_compute_global_forwarding_rule.frontend_http.ip_address
}

output "cdn_enabled" {
  description = "Whether CDN is enabled for the frontend"
  value       = google_compute_backend_bucket.frontend_backend.enable_cdn
}