variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "app_name" {
  description = "The name of the application"
  type        = string
  default     = "technology-risk-register"
}

variable "environment" {
  description = "The environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "domain_name" {
  description = "Custom domain name (optional)"
  type        = string
  default     = ""
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "cpu_limit" {
  description = "CPU limit for Cloud Run service"
  type        = string
  default     = "1"
}

variable "memory_limit" {
  description = "Memory limit for Cloud Run service"
  type        = string
  default     = "512Mi"
}

variable "allowed_origins" {
  description = "Additional CORS origins (e.g., custom domains). The Load Balancer IP is automatically included."
  type        = list(string)
  default     = []
}

variable "auth_username" {
  description = "Username for basic authentication"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "auth_password" {
  description = "Password for basic authentication"
  type        = string
  default     = ""  # Must be set in terraform.tfvars
  sensitive   = true
}

variable "auth_secret_key" {
  description = "Secret key for JWT token signing"
  type        = string
  default     = ""  # Must be set in terraform.tfvars
  sensitive   = true
}