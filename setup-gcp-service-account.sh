#!/bin/bash

# Technology Risk Register - GCP Service Account Setup for GitHub Actions
# This script creates a service account with necessary permissions for CI/CD deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
Technology Risk Register - GCP Service Account Setup

This script creates a service account for GitHub Actions with permissions to:
- Deploy to Cloud Run
- Push to Artifact Registry
- Manage Cloud Storage buckets
- Use service accounts

Usage: ./setup-gcp-service-account.sh [OPTIONS]

Options:
    -p, --project-id PROJECT_ID    GCP Project ID (required)
    -s, --sa-name NAME             Service account name (default: github-actions-deployer)
    -k, --key-file PATH            Output path for JSON key (default: ./github-actions-key.json)
    -h, --help                     Show this help message

Example:
    ./setup-gcp-service-account.sh --project-id my-gcp-project

After running this script:
1. Add the JSON key content to GitHub Secrets as 'GCP_SA_KEY'
2. Delete the local key file for security
3. Add other required secrets to GitHub (see documentation)

EOF
}

# Default values
PROJECT_ID=""
SA_NAME="github-actions-deployer"
KEY_FILE="./github-actions-key.json"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        -s|--sa-name)
            SA_NAME="$2"
            shift 2
            ;;
        -k|--key-file)
            KEY_FILE="$2"
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

log_info "Setting up GCP service account for GitHub Actions deployment..."
log_info "Project ID: $PROJECT_ID"
log_info "Service Account Name: $SA_NAME"
log_info "Key File: $KEY_FILE"
echo

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    log_error "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 &> /dev/null; then
    log_error "Not authenticated with gcloud. Run 'gcloud auth login' first."
    exit 1
fi

# Set the project
log_info "Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Construct service account email
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if service account already exists
if gcloud iam service-accounts describe $SA_EMAIL &> /dev/null; then
    log_warn "Service account $SA_EMAIL already exists."
    read -p "Do you want to create a new key for this account? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Skipping service account creation. To add IAM roles, rerun this script."
        exit 0
    fi
else
    # Create service account
    log_info "Creating service account: $SA_NAME..."
    gcloud iam service-accounts create $SA_NAME \
        --display-name="GitHub Actions Deployer" \
        --description="Service account for GitHub Actions to deploy to Cloud Run and manage GCP resources"

    log_success "Service account created: $SA_EMAIL"
fi

# Add IAM roles
log_info "Adding IAM roles to service account..."

# Cloud Run Admin - Deploy and manage Cloud Run services
log_info "Adding role: Cloud Run Admin..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.admin" \
    --condition=None

# Artifact Registry Writer - Push Docker images
log_info "Adding role: Artifact Registry Writer..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/artifactregistry.writer" \
    --condition=None

# Storage Admin - Manage Cloud Storage buckets (database backup, frontend hosting)
log_info "Adding role: Storage Admin..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin" \
    --condition=None

# Service Account User - Required to deploy Cloud Run services
log_info "Adding role: Service Account User..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None

log_success "IAM roles added successfully!"

# Create and download key
log_info "Creating service account key..."

# Check if key file already exists
if [[ -f "$KEY_FILE" ]]; then
    log_warn "Key file already exists at $KEY_FILE"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Skipping key creation."
        exit 0
    fi
fi

gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SA_EMAIL

log_success "Service account key created: $KEY_FILE"

echo
echo "========================================"
echo "  Service Account Setup Complete! ✓"
echo "========================================"
echo
log_info "Next steps:"
echo
echo "1. Add this key to GitHub Secrets:"
echo "   - Go to: https://github.com/YOUR_REPO/settings/secrets/actions"
echo "   - Click 'New repository secret'"
echo "   - Name: GCP_SA_KEY"
echo "   - Value: $(cat $KEY_FILE)"
echo
echo "2. Add other required GitHub Secrets:"
echo "   - GCP_PROJECT_ID: $PROJECT_ID"
echo "   - GCP_REGION: us-central1 (or your region)"
echo "   - GCP_ARTIFACT_REGISTRY: us-central1-docker.pkg.dev/$PROJECT_ID/technology-risk-register-repo"
echo "   - GCP_ASSETS_BUCKET: $PROJECT_ID-technology-risk-register-assets"
echo "   - AUTH_PASSWORD: (generate a secure password)"
echo "   - AUTH_SECRET_KEY: (run: openssl rand -hex 32)"
echo "   - ANTHROPIC_API_KEY: (should already exist)"
echo
echo "3. DELETE the local key file for security:"
echo "   rm $KEY_FILE"
echo
echo "4. Verify service account:"
echo "   gcloud iam service-accounts describe $SA_EMAIL"
echo
log_warn "IMPORTANT: The key file contains sensitive credentials!"
log_warn "Delete it after adding to GitHub Secrets: rm $KEY_FILE"
echo
