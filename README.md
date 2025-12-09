# Technology Risk Register

A modern web application for managing technology risks with executive dashboard reporting, built with FastAPI backend and SQLite database optimized for serverless deployment to GCP.

## Features

- **Risk Management**: Complete CRUD operations for technology risks
- **Executive Dashboard**: Real-time metrics and visualizations for decision makers
- **AI-Powered Risk Chat**: Natural language interface to query risks using Claude (Anthropic)
- **Audit Trail**: Full history tracking of risk changes
- **Intelligent Prioritization**: Smart risk sorting by rating, financial impact, and business service impact
- **Serverless Ready**: SQLite + Cloud Storage architecture for cost-effective GCP deployment

## Technology Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: SQLite (local development and GCP deployment)
- **ORM**: SQLAlchemy with Alembic migrations
- **Testing**: Pytest with coverage
- **Code Quality**: Black, Ruff, MyPy, pre-commit hooks
- **Deployment**: Docker, GCP Cloud Run, Cloud Storage, Terraform IaC

## Quick Start

### Prerequisites

- Python 3.12+
- [UV](https://docs.astral.sh/uv/) (recommended) or pip
- Docker (optional, for containerized development)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd technology-risk-register
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run database migrations**
   ```bash
   uv run alembic upgrade head
   ```

4. **Start the development server**
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
   ```

5. **Access the API**
   - API Documentation: http://localhost:8080/docs
   - Health Check: http://localhost:8080/health
   - Dashboard Data: http://localhost:8080/api/v1/dashboard

### Docker Development

1. **Set up environment variables** (required for Risk SME Chat)
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your Anthropic API key
   # Get your key from: https://console.anthropic.com/settings/keys
   nano .env
   ```

   📖 **[Environment Setup Guide](./ENV_SETUP.md)** - Detailed instructions for configuring API keys and secrets

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - API: http://localhost:8080
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8080/docs

## Development Commands

### Code Quality
```bash
# Format code
uv run black .
uv run ruff check --fix .

# Type checking
uv run mypy app/

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Testing
```bash
 # Run all unit tests (recommended)
uv run pytest --ignore=tests/integration -v

# Run all tests with coverage
uv run pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
uv run pytest tests/test_risks.py -v

# Run tests with coverage threshold
uv run pytest --cov=app --cov-fail-under=90
```

### Integration Testing
Integration tests verify end-to-end API functionality against a live server instance.

```bash
# Install test dependencies
uv sync --group test

# Start the API server (in separate terminal or background)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8080

# Option 1: Use the test runner script (recommended)
python run_integration_tests.py

# Option 2: Test against custom URL
python run_integration_tests.py --url http://localhost:8080

# Option 3: Skip health check
python run_integration_tests.py --no-health-check

# Option 4: Direct pytest execution
API_BASE_URL=http://localhost:8080 uv run pytest tests/integration/ -v
```

**Docker Integration Testing:**
```bash
# Start application with Docker
docker-compose up -d

# Run integration tests against Docker container
python run_integration_tests.py --url http://localhost:8080

# Clean up
docker-compose down
```

**Test Coverage:**
The integration tests verify:
- Health and documentation endpoints
- Dropdown values API (categories, filtering, grouping)
- Dashboard data aggregation
- Risk CRUD operations (create, read, update, delete)
- Search functionality with case-insensitive matching
- Sorting and pagination with validation
- Risk update/audit trail endpoints
- Comprehensive error handling (404, 405, 422)

### Database Management
```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## API Endpoints

### Risk Management
- `GET /api/v1/risks/` - List all risks with filtering
- `POST /api/v1/risks/` - Create new risk
- `GET /api/v1/risks/{risk_id}` - Get specific risk
- `PUT /api/v1/risks/{risk_id}` - Update risk
- `DELETE /api/v1/risks/{risk_id}` - Delete risk

### Risk SME Chat (AI-Powered)
- `POST /api/v1/chat/` - Ask natural language questions about risks
- `GET /api/v1/chat/health` - Check chat service health
- **Requires**: `ANTHROPIC_API_KEY` environment variable

### Dashboard
- `GET /api/v1/dashboard/` - Get complete dashboard data

### System
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

## Risk Data Model

### Core Fields
- **Risk ID**: Auto-generated (e.g., TR-2024-CYB-001)
- **Risk Assessment**: Probability × Impact ratings (1-5 scale)
- **Controls**: Preventative, Detective, Corrective status
- **Business Impact**: Financial estimates, RTO/RPO, IBS impact
- **Ownership**: Risk owner and department assignment

### Dashboard Metrics
The dashboard provides 9 key components:
1. Overall Risk Exposure Summary
2. Risk Distribution by Severity
3. Risk by Technology Domain
4. Control Posture Overview
5. Top 10 Highest Priority Risks
6. Risk Response Strategy Breakdown
7. Financial Impact Exposure
8. Risk Management Activity
9. Business Service Risk Exposure

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment.

### Pull Request Validation (CI)
When you open a pull request, the following checks run automatically:
- **Backend**: Black format check, Ruff linting, MyPy type checking, pytest with 90% coverage
- **Frontend**: ESLint, TypeScript type checking
- **Build Verification**: Docker image build, frontend build

All checks must pass before merging to `main`.

### Automated Deployment (CD)
On push to `main` branch, the pipeline automatically:
1. **Quality Checks**: Runs all linting, type checking, and tests
2. **Build Backend**: Builds Docker image and pushes to both:
   - GitHub Container Registry: `ghcr.io/sverze/technology-risk-register:latest`
   - GCP Artifact Registry: `[REGION]-docker.pkg.dev/[PROJECT]/technology-risk-register-repo`
3. **Deploy Backend**: Deploys to Cloud Run with environment variables
4. **Build Frontend**: Builds React app with Cloud Run API URL
5. **Verify Build**: Validates frontend contains correct `/api/v1` prefix
6. **Deploy Frontend**: Uploads static files to Cloud Storage bucket
7. **Health Check**: Verifies backend deployment is healthy

**Container Images:**
- Latest: `ghcr.io/sverze/technology-risk-register:latest`
- By commit: `ghcr.io/sverze/technology-risk-register:main-abc1234`
- By SHA: `ghcr.io/sverze/technology-risk-register:sha-abc1234`

**Setup Requirements:**
See [GCP Deployment Setup](#gcp-cloud-run-production) section below for GitHub secrets configuration.

## Deployment

### Local Development
The application runs with SQLite database file locally. Database is automatically created and seeded with dropdown values on startup.

```bash
# Start backend only
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Access at http://localhost:8080/docs
```

### Docker Desktop Deployment

Deploy the full stack (backend + frontend) locally using Docker Desktop.

#### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- `.env` file configured with `ANTHROPIC_API_KEY` (see [ENV_SETUP.md](./ENV_SETUP.md))

#### Deployment Steps

1. **Start Docker Desktop**
   - Ensure Docker Desktop is running
   - On macOS/Windows: Look for Docker icon in system tray
   - On Linux: `sudo systemctl start docker`

2. **Configure Environment** (optional, for AI chat feature)
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit and add your Anthropic API key
   nano .env  # or use your preferred editor
   ```

3. **Build and Start Containers**
   ```bash
   # Build images and start all services
   docker-compose up --build -d

   # View logs (optional)
   docker-compose logs -f
   ```

4. **Access the Application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8080/api/v1
   - **API Documentation**: http://localhost:8080/docs
   - **Health Check**: http://localhost:8080/health

5. **Verify Deployment**
   ```bash
   # Check containers are running
   docker-compose ps

   # Test backend health
   curl http://localhost:8080/health

   # View backend logs
   docker-compose logs backend

   # View frontend logs
   docker-compose logs frontend
   ```

#### Docker Commands

```bash
# Stop containers (preserves data)
docker-compose stop

# Start stopped containers
docker-compose start

# Restart containers (apply code changes)
docker-compose restart

# Stop and remove containers (clean slate)
docker-compose down

# Stop and remove containers + volumes (delete database)
docker-compose down -v

# Rebuild after code changes
docker-compose up --build -d

# View resource usage
docker stats
```

#### Troubleshooting Docker Desktop

**Port Already in Use:**
```bash
# Find what's using port 8080
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Kill the process or change docker-compose.yml ports
```

**Container Won't Start:**
```bash
# Check logs for errors
docker-compose logs backend

# Remove containers and start fresh
docker-compose down -v
docker-compose up --build
```

**Database Issues:**
```bash
# Reset database (warning: deletes all data)
docker-compose down -v
docker-compose up -d

# The database will be recreated and seeded automatically
```

**Performance Issues:**
```bash
# Check Docker Desktop resource allocation
# Settings → Resources → adjust CPU/Memory

# Recommended: 4GB RAM, 2 CPUs minimum
```

### GCP Cloud Run (Production)

**⭐ Primary Deployment Method: GitHub Actions (Automated)**

All production deployments should use the automated GitHub Actions pipeline. Simply push to the `main` branch to trigger deployment.

#### Automated Deployment Setup (One-Time)

1. **Create GCP Service Account**
   ```bash
   ./setup-gcp-service-account.sh --project-id your-gcp-project-id
   ```

2. **Configure GitHub Secrets**

   Go to GitHub Repository → Settings → Secrets and variables → Actions, and add:

   | Secret Name | Value | How to Get |
   |-------------|-------|------------|
   | `GCP_PROJECT_ID` | your-gcp-project-id | GCP Console → Project Info |
   | `GCP_SA_KEY` | {...} | Service account JSON key from step 1 |
   | `GCP_REGION` | us-central1 | Your preferred GCP region |
   | `GCP_ARTIFACT_REGISTRY` | us-central1-docker.pkg.dev/... | Run: `cd terraform && terraform output container_registry` |
   | `GCP_ASSETS_BUCKET` | your-project-assets | Run: `cd terraform && terraform output assets_bucket_name` |
   | `AUTH_PASSWORD` | SecurePassword123! | Generate a secure password |
   | `AUTH_SECRET_KEY` | [32+ char string] | Run: `openssl rand -hex 32` |
   | `ANTHROPIC_API_KEY` | sk-ant-... | Get from https://console.anthropic.com |

3. **Deploy Infrastructure** (if not already deployed)
   ```bash
   cd terraform
   terraform init
   terraform plan -var="project_id=your-gcp-project-id"
   terraform apply -var="project_id=your-gcp-project-id"
   cd ..
   ```

4. **Trigger Deployment**
   ```bash
   # Push to main branch to trigger automated deployment
   git push origin main

   # Monitor deployment: https://github.com/YOUR_REPO/actions
   ```

#### Deployment Architecture

**Backend (Cloud Run):**
- Docker image from GCP Artifact Registry
- Auto-scaling: 0-10 instances
- Memory: 512Mi, CPU: 1
- Port: 8080
- Database: SQLite synced to Cloud Storage

**Frontend (Cloud Storage + Load Balancer):**
- Static files hosted in Cloud Storage bucket
- CDN caching: 1 year for assets, 1 hour for HTML
- Served via HTTP Load Balancer with API proxying

**Features:**
- ✅ Automatic deployment on push to main
- ✅ Zero-downtime deployments
- ✅ Auto-scaling (pay-per-use)
- ✅ HTTPS with automatic SSL
- ✅ Health checks and validation
- ✅ Database persistence across deploys

#### Monitoring Production

```bash
# View Cloud Run logs
gcloud run services logs tail technology-risk-register --region=us-central1

# Check deployment status
gcloud run services describe technology-risk-register --region=us-central1

# View GitHub Actions workflow runs
# https://github.com/YOUR_REPO/actions
```

### Emergency Manual Deployment

**⚠️ Use ONLY when GitHub Actions is unavailable or for emergency hotfixes**

The manual deployment scripts are retained as fallback options:

```bash
# Manual backend deployment (skip if GitHub Actions works)
./deploy.sh --project-id your-gcp-project-id --skip-terraform

# Manual frontend deployment (skip if GitHub Actions works)
./deploy-frontend.sh --project-id your-gcp-project-id

# Manual Terraform operations (infrastructure changes)
cd terraform
terraform apply -var="project_id=your-gcp-project-id"
cd ..
```

**When to use manual scripts:**
- GitHub Actions is down or broken
- Testing infrastructure changes locally
- Emergency hotfix that can't wait for CI/CD
- Running Terraform for infrastructure updates

**Important**: For regular deployments, always use GitHub Actions by pushing to `main`.

### Environment Variables

**Local Development:**
```bash
DATABASE_URL=sqlite:///./risk_register.db
ALLOWED_ORIGINS=["http://localhost:3000"]
ANTHROPIC_API_KEY=sk-ant-...
```

**Docker Compose:**
See `.env.example` for configuration template.

**Cloud Run Production:**
Configured automatically by GitHub Actions CD workflow from repository secrets.

📖 **[Complete Deployment Guide](./DEPLOYMENT.md)** - Advanced configuration and troubleshooting

## Contributing

1. Follow the existing code style (Black + Ruff)
2. Ensure all tests pass with >90% coverage
3. Update documentation for new features
4. Use conventional commit messages
