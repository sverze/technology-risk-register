#!/bin/bash

# Technology Risk Register - GCP Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="prod"
PROJECT_ID=""
REGION="us-central1"
SKIP_TERRAFORM=false
SKIP_BUILD=false

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
Technology Risk Register - GCP Deployment Script

Usage: ./deploy.sh [OPTIONS]

Options:
    -p, --project-id PROJECT_ID    GCP Project ID (required)
    -r, --region REGION           GCP Region (default: us-central1)
    -e, --environment ENV         Environment (default: prod)
    --skip-terraform              Skip Terraform operations
    --skip-build                  Skip Docker build and push
    -h, --help                    Show this help message

Examples:
    ./deploy.sh --project-id my-gcp-project
    ./deploy.sh -p my-project -r europe-west1 -e staging
    ./deploy.sh -p my-project --skip-terraform

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
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --skip-terraform)
            SKIP_TERRAFORM=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
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

log_info "Starting deployment to GCP..."
log_info "Project ID: $PROJECT_ID"
log_info "Region: $REGION"
log_info "Environment: $ENVIRONMENT"

# Check prerequisites
log_info "Checking prerequisites..."

# Check if gcloud is installed and authenticated
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

# Check if Terraform is installed
if [[ "$SKIP_TERRAFORM" == false ]] && ! command -v terraform &> /dev/null; then
    log_error "Terraform is not installed. Please install it or use --skip-terraform."
    exit 1
fi

# Navigate to terraform directory
if [[ "$SKIP_TERRAFORM" == false ]]; then
    log_info "Deploying infrastructure with Terraform..."
    cd terraform

    # Check if terraform.tfvars exists
    if [[ ! -f "terraform.tfvars" ]]; then
        log_warn "terraform.tfvars not found. Creating from template..."
        cp terraform.tfvars.example terraform.tfvars
        sed -i.bak "s/your-gcp-project-id/$PROJECT_ID/g" terraform.tfvars
        sed -i.bak "s/us-central1/$REGION/g" terraform.tfvars
        rm terraform.tfvars.bak
        log_info "Please review and update terraform.tfvars before proceeding."
        read -p "Press Enter to continue after reviewing terraform.tfvars..."
    fi

    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init

    # Plan Terraform
    log_info "Planning Terraform deployment..."
    terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="environment=$ENVIRONMENT"

    # Apply Terraform
    read -p "Do you want to apply these changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Applying Terraform configuration..."
        terraform apply -auto-approve -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="environment=$ENVIRONMENT"
        log_success "Infrastructure deployed successfully!"
    else
        log_warn "Terraform apply cancelled."
        exit 1
    fi

    # Get outputs
    log_info "Getting Terraform outputs..."
    CONTAINER_REGISTRY=$(terraform output -raw container_registry)

    cd ..
else
    log_warn "Skipping Terraform deployment"
    CONTAINER_REGISTRY="$REGION-docker.pkg.dev/$PROJECT_ID/technology-risk-register-repo"
fi

# Build and push Docker image
if [[ "$SKIP_BUILD" == false ]]; then
    log_info "Building and pushing Docker image..."

    # Build backend-only Docker image with Cloud Build
    log_info "Submitting backend build to Cloud Build..."
    gcloud builds submit --config cloudbuild.yaml --substitutions=_CONTAINER_REGISTRY=$CONTAINER_REGISTRY .

    log_success "Backend Docker image built and pushed successfully!"
else
    log_warn "Skipping Docker build and push"
fi

# Get configuration from Terraform if available
CORS_ORIGINS="*"  # Default to allow all origins
DATABASE_URL="sqlite:///./risk_register.db"  # Default database URL
GCP_BUCKET_NAME=""  # Default to empty, will be set if available

if [[ "$SKIP_TERRAFORM" == false ]] && command -v terraform &> /dev/null && [[ -d "terraform" ]]; then
    cd terraform
    FRONTEND_IP=$(terraform output -raw frontend_ip 2>/dev/null || echo "")
    DATABASE_BUCKET_NAME=$(terraform output -raw database_bucket_name 2>/dev/null || echo "")
    cd ..

    # Set CORS origins if frontend IP is available
    if [[ -n "$FRONTEND_IP" ]]; then
        log_info "Configuring CORS for HTTP frontend IP: $FRONTEND_IP"
        # Use semicolon-separated values with alternate delimiter to avoid comma issues
        CORS_ORIGINS="^;^http://$FRONTEND_IP;http://localhost:3000;http://127.0.0.1:3000;http://localhost:8008;http://127.0.0.1:8008;http://frontend:3000"
    else
        log_warn "Could not determine frontend IP, using wildcard CORS"
        CORS_ORIGINS="*"
    fi

    # Set GCS bucket name if available
    if [[ -n "$DATABASE_BUCKET_NAME" ]]; then
        GCP_BUCKET_NAME="$DATABASE_BUCKET_NAME"
        log_info "Using database bucket: $GCP_BUCKET_NAME"
    else
        log_warn "Could not determine database bucket name"
    fi
else
    log_warn "Terraform not available, using wildcard CORS"
    CORS_ORIGINS="*"
fi

# Deploy to Cloud Run
log_info "Deploying backend to Cloud Run..."

# Build environment variables string
ENV_VARS="GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=$ENVIRONMENT,ALLOWED_ORIGINS=$CORS_ORIGINS,DATABASE_URL=$DATABASE_URL"
if [[ -n "$GCP_BUCKET_NAME" ]]; then
    ENV_VARS="$ENV_VARS,GCP_BUCKET_NAME=$GCP_BUCKET_NAME"
fi

gcloud run deploy technology-risk-register \
    --image $CONTAINER_REGISTRY/technology-risk-register:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout=300 \
    --cpu-boost \
    --cpu-throttling \
    --set-env-vars "$ENV_VARS"

# Get the service URL
SERVICE_URL=$(gcloud run services describe technology-risk-register --region=$REGION --format="value(status.url)")

log_success "Backend deployed to Cloud Run successfully!"

# Deploy frontend to Cloud Storage + CDN
log_info "Deploying frontend to Cloud Storage + CDN..."

# Check if frontend deployment script exists
if [[ -f "./deploy-frontend.sh" ]]; then
    # Make it executable if not already
    chmod +x ./deploy-frontend.sh

    # Deploy frontend
    ./deploy-frontend.sh --project-id $PROJECT_ID --region $REGION

    log_success "Frontend deployed to Cloud Storage + CDN successfully!"
else
    log_warn "Frontend deployment script not found. Skipping frontend deployment."
    log_info "To deploy frontend manually, run: ./deploy-frontend.sh --project-id $PROJECT_ID"
fi

log_success "Deployment completed successfully!"

# Display service URLs
log_success "Backend API URL: $SERVICE_URL"
log_info "API Documentation: $SERVICE_URL/docs"
log_info "Health Check: $SERVICE_URL/health"

# Get frontend URL from Terraform if available
if [[ "$SKIP_TERRAFORM" == false ]] && command -v terraform &> /dev/null && [[ -d "terraform" ]]; then
    cd terraform
    FRONTEND_URL=$(terraform output -raw frontend_url 2>/dev/null || echo "")
    cd ..
    if [[ -n "$FRONTEND_URL" ]]; then
        log_success "Frontend URL: $FRONTEND_URL"
        log_info "Frontend is served via Cloud Storage + CDN with API proxying"
    fi
fi

# Test the deployment
log_info "Testing backend deployment..."
if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    log_success "Backend health check passed!"
else
    log_warn "Backend health check failed. Please check the logs."
    log_info "View logs with: gcloud run services logs tail technology-risk-register --region=$REGION"
fi

log_success "Deployment script completed!"
