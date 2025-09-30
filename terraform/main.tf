# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "storage.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com"
  ])

  service = each.value
  disable_on_destroy = false
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "container_repo" {
  location      = var.region
  repository_id = "${var.app_name}-repo"
  description   = "Container registry for ${var.app_name}"
  format        = "DOCKER"

  depends_on = [google_project_service.required_apis]
}

# Cloud Storage bucket for SQLite database
resource "google_storage_bucket" "database_bucket" {
  name     = "${var.project_id}-${var.app_name}-database"
  location = var.region

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy = true  # Allow deletion even with objects

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
      num_newer_versions = 5
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud Storage bucket for frontend assets
resource "google_storage_bucket" "assets_bucket" {
  name     = "${var.project_id}-${var.app_name}-assets"
  location = var.region

  uniform_bucket_level_access = true
  public_access_prevention    = "inherited"
  force_destroy = true  # Allow deletion even with objects

  # Enable website hosting
  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"  # For SPA routing
  }

  # CORS configuration for frontend assets
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  depends_on = [google_project_service.required_apis]
}

# Service account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "tech-risk-sa"
  display_name = "Cloud Run Service Account for ${var.app_name}"
}

# IAM bindings for service account
resource "google_storage_bucket_iam_member" "database_bucket_access" {
  bucket = google_storage_bucket.database_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_storage_bucket_iam_member" "assets_bucket_access" {
  bucket = google_storage_bucket.assets_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Make assets bucket publicly readable for CDN
resource "google_storage_bucket_iam_member" "assets_bucket_public" {
  bucket = google_storage_bucket.assets_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Cloud CDN Backend Bucket
resource "google_compute_backend_bucket" "frontend_backend" {
  name        = "${var.app_name}-frontend-backend"
  bucket_name = google_storage_bucket.assets_bucket.name
  enable_cdn  = true

  cdn_policy {
    cache_mode                   = "CACHE_ALL_STATIC"
    default_ttl                  = 3600
    max_ttl                      = 86400
    client_ttl                   = 3600
    negative_caching             = true
    serve_while_stale            = 86400
  }

  depends_on = [google_project_service.required_apis]
}

# URL Map for Load Balancer
resource "google_compute_url_map" "frontend_url_map" {
  name            = "${var.app_name}-url-map"
  default_service = google_compute_backend_bucket.frontend_backend.id

  # Route API requests to Cloud Run backend
  host_rule {
    hosts        = ["*"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_bucket.frontend_backend.id

    # API routes go to Cloud Run
    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.api_backend.id
    }

    # Everything else goes to frontend (Cloud Storage)
    path_rule {
      paths   = ["/*"]
      service = google_compute_backend_bucket.frontend_backend.id
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Backend service for API (Cloud Run)
resource "google_compute_backend_service" "api_backend" {
  name                  = "${var.app_name}-api-backend"
  protocol              = "HTTP"
  timeout_sec           = 30
  enable_cdn            = false
  load_balancing_scheme = "EXTERNAL"

  backend {
    group = "https://www.googleapis.com/compute/v1/projects/${var.project_id}/regions/${var.region}/networkEndpointGroups/${google_compute_region_network_endpoint_group.api_neg.name}"
  }

  depends_on = [google_project_service.required_apis]
}

# Network Endpoint Group for Cloud Run
resource "google_compute_region_network_endpoint_group" "api_neg" {
  name                  = "${var.app_name}-api-neg"
  region                = var.region
  network_endpoint_type = "SERVERLESS"

  cloud_run {
    service = var.app_name
  }

  depends_on = [google_project_service.required_apis]
}

# HTTPS Target Proxy (only if SSL certificate exists)
resource "google_compute_target_https_proxy" "frontend_https_proxy" {
  count   = var.domain_name != "" ? 1 : 0
  name    = "${var.app_name}-https-proxy"
  url_map = google_compute_url_map.frontend_url_map.id

  ssl_certificates = [google_compute_managed_ssl_certificate.frontend_ssl[0].id]

  depends_on = [google_project_service.required_apis]
}

# Managed SSL Certificate (only if domain is provided)
resource "google_compute_managed_ssl_certificate" "frontend_ssl" {
  count = var.domain_name != "" ? 1 : 0
  name  = "${var.app_name}-ssl-cert"

  managed {
    domains = [var.domain_name]
  }

  depends_on = [google_project_service.required_apis]
}

# Global Forwarding Rule (HTTPS - only if SSL certificate exists)
resource "google_compute_global_forwarding_rule" "frontend_https" {
  count      = var.domain_name != "" ? 1 : 0
  name       = "${var.app_name}-https-forwarding-rule"
  target     = google_compute_target_https_proxy.frontend_https_proxy[0].id
  port_range = "443"

  depends_on = [google_project_service.required_apis]
}

# HTTP to HTTPS Redirect (only if HTTPS is available)
resource "google_compute_url_map" "https_redirect" {
  count = var.domain_name != "" ? 1 : 0
  name  = "${var.app_name}-https-redirect"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }

  depends_on = [google_project_service.required_apis]
}

# HTTP Target Proxy
resource "google_compute_target_http_proxy" "frontend_http_proxy" {
  name    = "${var.app_name}-http-proxy"
  url_map = var.domain_name != "" ? google_compute_url_map.https_redirect[0].id : google_compute_url_map.frontend_url_map.id

  depends_on = [google_project_service.required_apis]
}

resource "google_compute_global_forwarding_rule" "frontend_http" {
  name       = "${var.app_name}-http-forwarding-rule"
  target     = google_compute_target_http_proxy.frontend_http_proxy.id
  port_range = "80"

  depends_on = [google_project_service.required_apis]
}

# Cloud Run service with GCS volume mount
resource "google_cloud_run_v2_service" "app" {
  provider = google-beta
  name     = var.app_name
  location = var.region

  template {
    service_account = google_service_account.cloud_run_sa.email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = "gcr.io/cloudrun/hello"

      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
      }

      ports {
        container_port = 8080
      }

      env {
        name  = "DATABASE_URL"
        value = "sqlite:///./risk_register.db"
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCP_BUCKET_NAME"
        value = google_storage_bucket.database_bucket.name
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [google_project_service.required_apis]

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# Cloud Run IAM policy for public access
resource "google_cloud_run_v2_service_iam_binding" "public_access" {
  location = google_cloud_run_v2_service.app.location
  project  = google_cloud_run_v2_service.app.project
  name     = google_cloud_run_v2_service.app.name
  role     = "roles/run.invoker"

  members = [
    "allUsers",
  ]
}

# Custom domain mapping (optional)
resource "google_cloud_run_domain_mapping" "domain" {
  count = var.domain_name != "" ? 1 : 0

  location = var.region
  name     = var.domain_name

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.app.name
  }
}
