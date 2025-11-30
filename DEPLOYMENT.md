# Technology Risk Register - GCP Deployment Guide

This guide walks you through deploying the Technology Risk Register application to Google Cloud Platform using Infrastructure as Code (Terraform) and Cloud Run.

## Architecture Overview

The application is deployed on GCP with the following components:

- **Cloud Run**: Serverless container platform hosting the combined React frontend and FastAPI backend
- **Cloud Storage**: Stores the SQLite database file with automatic sync
- **Artifact Registry**: Container registry for Docker images
- **Cloud Build**: Automated Docker image building

## Prerequisites

### 1. Install Required Tools

```bash
# Install Google Cloud CLI
# macOS (using Homebrew)
brew install --cask google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install

# Install Terraform
brew install terraform

# Verify installations
gcloud --version
terraform --version
```

### 2. Set up GCP Project

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set your project ID (replace YOUR_PROJECT_ID)
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Set up application default credentials for Terraform
gcloud auth application-default login
```

## Deployment Methods

### Method 1: Quick Deployment (Recommended)

Use the automated deployment script:

```bash
# Basic deployment
./deploy.sh --project-id your-project-id

# Custom region and environment
./deploy.sh --project-id your-project-id --region europe-west1 --environment staging

# Skip Terraform (if infrastructure already exists)
./deploy.sh --project-id your-project-id --skip-terraform

# Skip build (if image already exists)
./deploy.sh --project-id your-project-id --skip-build
```

#### Frontend Deployment

After deploying the backend infrastructure, deploy the frontend:

```bash
# Deploy React frontend to Cloud Storage + Load Balancer
./deploy-frontend.sh --project-id your-project-id --region us-central1

# The script will:
# 1. Build the React application for production
# 2. Configure API endpoints to use the deployed backend
# 3. Upload static files to Cloud Storage bucket
# 4. Configure Load Balancer for HTTP access
# 5. Display the frontend URL for access
```

### Method 2: Manual Step-by-Step Deployment

#### Step 1: Configure Terraform

```bash
cd terraform

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
project_id = "your-project-id"
region = "us-central1"
environment = "prod"
# ... other optional variables
```

#### Step 2: Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the infrastructure
terraform apply
```

#### Step 3: Build and Deploy Application

```bash
# Return to project root
cd ..

# Build and push Docker image using Cloud Build
PROJECT_ID=$(cd terraform && terraform output -raw project_id)
REGION=$(cd terraform && terraform output -raw region)
REGISTRY=$(cd terraform && terraform output -raw container_registry)

gcloud builds submit --tag $REGISTRY/technology-risk-register:latest .

# Deploy to Cloud Run
gcloud run deploy technology-risk-register \
    --image $REGISTRY/tech-risk-register:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=prod
```

## Configuration

### Environment Variables

The application supports the following environment variables for production:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GCP_PROJECT_ID` | Your GCP project ID | - | Yes |
| `GCP_BUCKET_NAME` | Cloud Storage bucket for database | Auto-generated | No |
| `ALLOWED_ORIGINS` | JSON array of allowed CORS origins | Development defaults | No |
| `DATABASE_URL` | SQLite database path | `./risk_register.db` | No |
| `ENVIRONMENT` | Environment name | `prod` | No |

### Terraform Variables

Configure these in `terraform/terraform.tfvars`:

```hcl
# Required
project_id = "your-gcp-project-id"

# Required: Authentication & API Keys
auth_username = "admin"
auth_password = "your-secure-password-here"     # Minimum 8 characters
auth_secret_key = "your-secret-key-here"         # Generate with: openssl rand -hex 32
anthropic_api_key = "sk-ant-api03-your-key-here" # Get from: https://console.anthropic.com/settings/keys

# Optional
region = "us-central1"
app_name = "tech-risk-register"
environment = "prod"
domain_name = "your-custom-domain.com"  # Optional custom domain
min_instances = 0
max_instances = 10
cpu_limit = "1"
memory_limit = "512Mi"
allowed_origins = ["https://your-domain.com"]
```

## Database Management

The application automatically syncs the SQLite database with Cloud Storage:

- **Startup**: Downloads the latest database from Cloud Storage
- **Shutdown**: Uploads the current database to Cloud Storage
- **Manual Sync**: Use admin endpoints for manual synchronization

### Admin Endpoints

Access these endpoints for database management:

```bash
# Get Cloud Storage status
curl https://your-app-url/api/v1/admin/cloud-storage-status

# Manually sync database to Cloud Storage
curl -X POST https://your-app-url/api/v1/admin/sync-database

# Download database from Cloud Storage
curl -X POST https://your-app-url/api/v1/admin/download-database
```

## Monitoring and Logs

### View Application Logs

```bash
# Real-time logs
gcloud run services logs tail tech-risk-register --region=us-central1

# Historical logs
gcloud run services logs read tech-risk-register --region=us-central1 --limit=50
```

### Health Checks

The application provides health check endpoints:

- **Basic Health**: `GET /health`
- **API Health**: `GET /api/v1/health` (if implemented)

### Monitoring in GCP Console

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click on your service
3. Navigate to "Metrics" tab for monitoring
4. Use "Logs" tab for detailed application logs

## Custom Domain Setup (Optional)

If you specified a `domain_name` in your Terraform variables:

1. **Verify domain ownership** in [Google Search Console](https://search.google.com/search-console)

2. **Update DNS records** to point to Cloud Run:
   ```
   CNAME your-domain.com ghs.googlehosted.com
   ```

3. **SSL certificate** is automatically provisioned by Google

## Scaling and Performance

### Auto-scaling Configuration

The deployment is configured with:
- **Min instances**: 0 (scales to zero when not in use)
- **Max instances**: 10 (prevents runaway costs)
- **CPU**: 1 vCPU per instance
- **Memory**: 512Mi per instance

### Cost Optimization

- **Pay per use**: Only pay when the application is processing requests
- **Cold starts**: ~2-3 seconds when scaling from zero
- **Database**: SQLite file stored in Cloud Storage (minimal cost)

## Troubleshooting

### Common Issues

#### 1. Permission Errors
```bash
# Ensure proper authentication
gcloud auth login
gcloud auth application-default login

# Check project permissions
gcloud projects get-iam-policy $PROJECT_ID
```

#### 2. API Not Enabled
```bash
# Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com storage.googleapis.com artifactregistry.googleapis.com
```

#### 3. Build Failures
```bash
# Check Cloud Build logs
gcloud builds list --limit=5

# View specific build
gcloud builds log [BUILD_ID]
```

#### 4. Service Not Starting
```bash
# Check service status
gcloud run services describe tech-risk-register --region=us-central1

# View service logs
gcloud run services logs tail tech-risk-register --region=us-central1
```

### Database Issues

#### Reset Database
```bash
# Delete database from Cloud Storage (caution: data loss!)
gsutil rm gs://your-bucket-name/risk_register.db

# Restart the service to create fresh database
gcloud run services update technology-risk-register --region=us-central1
```

## Security Considerations

- **HTTPS**: All traffic is automatically encrypted
- **IAM**: Service uses least-privilege service account
- **CORS**: Configure allowed origins appropriately
- **Database**: SQLite file is private in Cloud Storage
- **No Secrets**: No hardcoded credentials in code

## Maintenance

### Update Application

```bash
# Re-run deployment script
./deploy.sh --project-id your-project-id

# Or manually rebuild and deploy
gcloud builds submit --tag $REGISTRY/technology-risk-register:latest .
gcloud run deploy technology-risk-register --image $REGISTRY/tech-risk-register:latest --region us-central1
```

### Backup Database

```bash
# Download current database
gsutil cp gs://your-bucket-name/risk_register.db ./backup-$(date +%Y%m%d).db
```

### Destroy Infrastructure

**Quick Destroy:**
```bash
cd terraform
terraform destroy -auto-approve
```

**Safe Destroy (with confirmation):**
```bash
cd terraform
terraform destroy

# You'll be prompted to confirm before deletion
# Type "yes" to proceed
```

**What gets destroyed:**
- Cloud Run service (backend API)
- Global Load Balancer (frontend)
- Cloud Storage bucket (including database file!)
- Artifact Registry repository
- All associated networking and security resources

⚠️ **Warning**: This will delete all resources and data. Ensure you have backups!

**Backup database before destroying:**
```bash
# Download current database
PROJECT_ID="your-project-id"
gsutil cp gs://$PROJECT_ID-technology-risk-register-assets/risk_register.db ./backup-$(date +%Y%m%d).db
```

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review [Cloud Run documentation](https://cloud.google.com/run/docs)
3. Check application logs for specific error messages