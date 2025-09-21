# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Technology Risk Register Application

This is a web application for managing technology risks with a dashboard view and tabular entries view. Built with FastAPI backend, React frontend, and SQLite database that deploys serverlessly to GCP.

## Development Commands

### Backend Development
```bash
# Run the development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8008

# Run tests with coverage
uv run pytest --cov=app --cov-report=html --cov-report=term

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
# - Backend API: http://localhost:8008/api/v1
# - API Docs: http://localhost:8008/docs
```

### GCP Deployment
```bash
# Quick deployment to GCP (after setting up gcloud auth)
./deploy.sh --project-id your-gcp-project-id

# Deploy with custom settings
./deploy.sh --project-id your-project --region europe-west1 --environment staging

# Skip Terraform (if infrastructure already exists)
./deploy.sh --project-id your-project --skip-terraform

# Manual Terraform operations
cd terraform
terraform init
terraform plan -var="project_id=your-project-id"
terraform apply -var="project_id=your-project-id"

# Manual Cloud Run deployment
make deploy  # (from terraform directory)

# View logs from deployed service
gcloud run services logs tail tech-risk-register --region=us-central1
```

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
- **GCP Production**: Cloud Run + Cloud Storage for SQLite + Terraform IaC
  - Container Registry: Artifact Registry for Docker images
  - Database: SQLite file synced with Cloud Storage bucket
  - Scaling: 0-10 instances, pay-per-use pricing
  - HTTPS: Automatic SSL certificates, custom domain support
  - Database migrations run automatically on startup
  - Admin endpoints: `/api/v1/admin/` for database management
- Environment variables for configuration
- When confronted with UI related issues consider using playwright to test and diagnose the issue
