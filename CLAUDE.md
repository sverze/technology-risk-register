# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Technology Risk Register Application

This is a web application for managing technology risks with a dashboard view and tabular entries view. Built with FastAPI backend, React frontend, and SQLite database that deploys serverlessly to GCP.

## Development Commands

### Backend Development
```bash
# Run the development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

 # Run all unit tests (recommended)
uv run pytest --ignore=tests/integration -v

# Run specific test file
uv run pytest tests/test_risks.py -v

# Run database migrations
uv run alembic upgrade head

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Format code
uv run black .
uv run ruff check --fix .

# Type checking
uv run mypy app/
```

### Docker Development
```bash
# Start local development environment (both frontend and backend)
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View all logs
docker-compose logs -f

# Rebuild containers after code changes
docker-compose up -d --build

# Stop and clean up
docker-compose down -v

# Access services:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8080/api/v1
# - API Docs: http://localhost:8080/docs
```

### GCP Deployment

**Primary Method: GitHub Actions (Automated)**

All deployments to production should use the automated GitHub Actions pipeline. Manual scripts are available as fallback options only.

#### Automated Deployment (GitHub Actions)

**Prerequisites** (one-time setup):
```bash
# 1. Create GCP service account and configure IAM roles
./setup-gcp-service-account.sh --project-id your-gcp-project-id

# 2. Add required secrets to GitHub repository settings:
#    - GCP_PROJECT_ID
#    - GCP_SA_KEY (JSON key from step 1)
#    - GCP_REGION (e.g., us-central1)
#    - GCP_ARTIFACT_REGISTRY
#    - GCP_ASSETS_BUCKET
#    - AUTH_PASSWORD
#    - AUTH_SECRET_KEY (generate with: openssl rand -hex 32)
#    - ANTHROPIC_API_KEY
```

**Deployment Process**:
- Push to `main` branch → Automatic deployment to production
- GitHub Actions workflow:
  1. Lint & test backend and frontend
  2. Build Docker image → Push to Artifact Registry
  3. Deploy backend → Cloud Run
  4. Build frontend with backend API URL
  5. Deploy frontend → Cloud Storage
  6. Health checks and validation

**Monitoring**:
```bash
# View Cloud Run logs
gcloud run services logs tail technology-risk-register --region=us-central1

# Check deployment status
gcloud run services describe technology-risk-register --region=us-central1

# View GitHub Actions workflow runs
# Go to: https://github.com/YOUR_REPO/actions
```

#### Manual Deployment (Emergency Fallback Only)

**⚠️ Use only when GitHub Actions is unavailable or for local testing**

The manual deployment scripts are retained for:
- Emergency hotfixes when GitHub Actions is down
- Local infrastructure testing
- Manual Terraform operations (infrastructure is still managed locally)

```bash
# Manual backend deployment (emergency only)
./deploy.sh --project-id your-gcp-project-id --skip-terraform

# Manual frontend deployment (emergency only)
./deploy-frontend.sh --project-id your-gcp-project-id

# Manual Terraform operations (infrastructure changes)
cd terraform
terraform init
terraform plan -var="project_id=your-project-id"
terraform apply -var="project_id=your-project-id"
cd ..
```

**Note**: For regular deployments, always use GitHub Actions by pushing to the `main` branch.

#### Deployment Architecture

**Backend** (Cloud Run):
- Docker image from Artifact Registry
- Auto-scaling: 0-10 instances
- Memory: 512Mi, CPU: 1
- Port: 8080
- Database: SQLite synced to Cloud Storage

**Frontend** (Cloud Storage + CDN):
- Static files hosted in Cloud Storage bucket
- CDN caching: 1 year for assets, 1 hour for HTML
- Served via Load Balancer with API proxying

**Database Persistence**:
- SQLite file backed up to Cloud Storage on every write
- Automatic download on container startup
- Versioned (5 versions retained for 30 days)

## Architecture Overview

### Backend Structure
- `app/main.py` - FastAPI application entry point
- `app/api/` - API route handlers organized by domain
- `app/models/` - SQLAlchemy database models
- `app/schemas/` - Pydantic models for request/response validation
- `app/core/` - Core utilities (database, config, security)
- `app/services/` - Business logic layer
- `alembic/` - Database migration files

### Database Design
- Uses SQLite for both local development and GCP deployment
- Primary tables: `risks`, `risk_updates`, `dropdown_values`
- Risk ratings are auto-calculated from probability × impact
- Full audit trail via risk_updates table

### Key Business Logic
- Risk rating calculation: `inherent_probability * inherent_impact` and `current_probability * current_impact`
- Risk priorities sorted by: Current Risk Rating DESC, Financial Impact High DESC, IBS Impact DESC
- Dashboard aggregations optimized for executive reporting

### Testing Standards
- Minimum 90% code coverage required
- Unit tests for all business logic in `services/`
- Integration tests for API endpoints
- Use pytest fixtures for database setup
- Mock external dependencies (Cloud Storage)

### Code Quality Tools
- Black for code formatting
- Ruff for linting and import sorting
- MyPy for type checking
- Pre-commit hooks enforce standards before commits

### Deployment
- **Local**: SQLite database file, Docker Compose for full stack
- **GCP Production**: Cloud Run + Cloud Storage sync for SQLite + Terraform IaC
  - Container Registry: Artifact Registry for Docker images
  - Database: SQLite with sync-on-write to Cloud Storage bucket for persistence
  - Data Persistence: `@sync_database_after_write` decorator ensures data persists across container restarts
  - Startup: Downloads existing database from Cloud Storage on container start
  - Scaling: 0-10 instances, pay-per-use pricing
  - HTTPS: Automatic SSL certificates, custom domain support
  - Database migrations run automatically on startup
  - Admin endpoints: `/api/v1/admin/` for database management and diagnostics
- Environment variables for configuration
- When confronted with UI related issues consider using playwright to test and diagnose the issue

### Terraform Conventions
**Files that should NOT be committed to git:**
- `*.tfstate` and `*.tfstate.*` - Contains sensitive infrastructure state and resource IDs
- `*.tfvars` - Contains sensitive configuration values (project IDs, secrets)
- `.terraform/` directory - Provider cache and temporary files
- `.terraform.lock.hcl` - Provider version locks (team decision - some commit, some don't)
- `*.tfplan` files - Plan files may contain sensitive data
- `crash.log` - Terraform crash logs

**Files that SHOULD be committed:**
- `*.tf` files - Infrastructure as code (main.tf, variables.tf, outputs.tf, etc.)
- `terraform.tfvars.example` - Template showing required variables
- `versions.tf` - Provider version constraints
- `README.md`, `Makefile` - Documentation and automation

**Security practices:**
- Store actual tfvars files outside the repository or use environment variables
- Use remote state backend (GCS, S3) for production deployments
- Keep sensitive values in CI/CD secrets or external key management
- Never commit state files - they contain actual resource identifiers and configuration
- Run all python unit tests before any commit using 'uv run pytest --ignore=tests/integration -v'
- The Git SSH config you must use is github.com-personal, prepend this on all interactions with GitHub
- The server runs on port 8080 in all environments (local, docker, Cloud Run)
