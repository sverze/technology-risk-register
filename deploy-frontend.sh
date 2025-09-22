#!/bin/bash

# Technology Risk Register - Frontend Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PROJECT_ID=""
REGION="us-central1"
ASSETS_BUCKET=""

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
Technology Risk Register - Frontend Deployment Script

Usage: ./deploy-frontend.sh [OPTIONS]

Options:
    -p, --project-id PROJECT_ID    GCP Project ID (required)
    -r, --region REGION           GCP Region (default: us-central1)
    -h, --help                    Show this help message

Examples:
    ./deploy-frontend.sh --project-id my-gcp-project
    ./deploy-frontend.sh -p my-project -r europe-west1

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$PROJECT_ID" ]]; then
    log_error "Project ID is required. Use -p or --project-id"
    show_help
    exit 1
fi

log_info "Starting frontend deployment to GCP..."
log_info "Project ID: $PROJECT_ID"
log_info "Region: $REGION"

# Check prerequisites
log_info "Checking prerequisites..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    log_error "gcloud CLI is not installed. Please install it first."
    exit 1
fi


# Check if npm is installed
if ! command -v npm &> /dev/null; then
    log_error "npm is not installed. Please install Node.js and npm first."
    exit 1
fi

# Set the project
log_info "Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Auto-detect assets bucket if not provided
if [[ -z "$ASSETS_BUCKET" ]]; then
    log_info "Auto-detecting assets bucket..."
    ASSETS_BUCKET="${PROJECT_ID}-technology-risk-register-assets"
    log_info "Using bucket: $ASSETS_BUCKET"
fi

# Check if assets bucket exists
if ! gsutil ls -b "gs://$ASSETS_BUCKET" &> /dev/null; then
    log_error "Assets bucket 'gs://$ASSETS_BUCKET' does not exist."
    log_error "Make sure Terraform has been applied to create the infrastructure."
    exit 1
fi

# Build the frontend
log_info "Building React frontend..."
cd frontend

# Install dependencies
log_info "Installing dependencies..."
npm ci

# Set production environment variables
export NODE_ENV=production

# Configure API base URL to use Cloud Run's native HTTPS
log_info "Configuring secure API base URL..."
if command -v terraform &> /dev/null && [[ -d "../terraform" ]]; then
    cd ../terraform
    CLOUD_RUN_URL=$(terraform output -raw cloud_run_url 2>/dev/null || echo "")
    cd ../frontend
    if [[ -n "$CLOUD_RUN_URL" ]]; then
        export VITE_API_BASE_URL="$CLOUD_RUN_URL/api/v1"
        log_info "Using secure API base URL: $VITE_API_BASE_URL"
    else
        log_warn "Could not determine Cloud Run URL, using default API configuration"
    fi
else
    log_warn "Terraform not available, using default API configuration"
fi

# Build the production bundle
log_info "Building production bundle..."
npm run build

log_success "Frontend build completed!"

# Deploy to Cloud Storage with Load Balancer
log_info "Uploading frontend to Cloud Storage..."

# Navigate back to project root
cd ..

# Upload to Cloud Storage bucket
log_info "Uploading build files to bucket gs://$ASSETS_BUCKET..."
gsutil -o "GSUtil:parallel_process_count=1" -m rsync -r -d frontend/dist gs://$ASSETS_BUCKET/

# Set proper content types (bucket is already publicly readable via IAM)
log_info "Setting file metadata..."

# Set metadata for specific files that exist
if gsutil ls gs://$ASSETS_BUCKET/assets/*.css >/dev/null 2>&1; then
    gsutil -o "GSUtil:parallel_process_count=1" -m setmeta -h "Content-Type:text/css" -h "Cache-Control:public,max-age=31536000" gs://$ASSETS_BUCKET/assets/*.css
fi

if gsutil ls gs://$ASSETS_BUCKET/assets/*.js >/dev/null 2>&1; then
    gsutil -o "GSUtil:parallel_process_count=1" -m setmeta -h "Content-Type:application/javascript" -h "Cache-Control:public,max-age=31536000" gs://$ASSETS_BUCKET/assets/*.js
fi

if gsutil ls gs://$ASSETS_BUCKET/*.html >/dev/null 2>&1; then
    gsutil -o "GSUtil:parallel_process_count=1" -m setmeta -h "Content-Type:text/html" -h "Cache-Control:public,max-age=3600" gs://$ASSETS_BUCKET/*.html
fi

if gsutil ls gs://$ASSETS_BUCKET/*.svg >/dev/null 2>&1; then
    gsutil -o "GSUtil:parallel_process_count=1" -m setmeta -h "Content-Type:image/svg+xml" -h "Cache-Control:public,max-age=31536000" gs://$ASSETS_BUCKET/*.svg
fi

log_success "Frontend uploaded to Cloud Storage successfully!"

# Get frontend URL from Terraform if available
if command -v terraform &> /dev/null && [[ -d "terraform" ]]; then
    cd terraform
    FRONTEND_URL=$(terraform output -raw frontend_url 2>/dev/null || echo "")
    FRONTEND_IP=$(terraform output -raw frontend_ip 2>/dev/null || echo "")
    cd ..

    if [[ -n "$FRONTEND_URL" ]]; then
        log_info "Frontend is available at:"
        log_success "$FRONTEND_URL"
    elif [[ -n "$FRONTEND_IP" ]]; then
        log_info "Frontend is available at:"
        log_success "http://$FRONTEND_IP"
        log_warn "Note: Using HTTP. For HTTPS, configure a custom domain in terraform.tfvars"
    else
        log_warn "Could not determine frontend URL from Terraform outputs"
        log_info "Check: https://console.cloud.google.com/storage/browser/$ASSETS_BUCKET"
    fi
else
    log_warn "Terraform not available to get frontend URL"
    log_info "Frontend files uploaded to: gs://$ASSETS_BUCKET/"
fi

log_success "Frontend deployment completed!"

# Script completed