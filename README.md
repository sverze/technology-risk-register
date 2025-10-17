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
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Dashboard Data: http://localhost:8000/api/v1/dashboard

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
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Option 1: Use the test runner script (recommended)
python run_integration_tests.py

# Option 2: Test against custom URL
python run_integration_tests.py --url http://localhost:8001

# Option 3: Skip health check
python run_integration_tests.py --no-health-check

# Option 4: Direct pytest execution
API_BASE_URL=http://localhost:8000 uv run pytest tests/integration/ -v
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

## Deployment

### Local Development
The application runs with SQLite database file locally. Database is automatically created and seeded with dropdown values on startup.

### GCP Cloud Run (Production)

**Quick Deployment:**
```bash
# Deploy backend infrastructure and API
./deploy.sh --project-id your-gcp-project-id

# Deploy frontend to Cloud Storage + Load Balancer
./deploy-frontend.sh --project-id your-gcp-project-id

# Custom region and environment
./deploy.sh --project-id your-project --region europe-west1 --environment staging
```

**Architecture:**
- **Backend**: Cloud Run (FastAPI API, HTTPS)
- **Frontend**: Cloud Storage + Global Load Balancer (React SPA, HTTP)
- **Database**: SQLite file with Cloud Storage sync
- **Container Registry**: Artifact Registry for Docker images
- **Infrastructure**: Terraform IaC for reproducible deployments

**Deployed Services:**
- **Frontend URL**: `http://[LOAD_BALANCER_IP]/` (shown after deployment)
- **Backend API**: `https://[CLOUD_RUN_URL]/api/v1/` (HTTPS with automatic SSL)
- **API Documentation**: `https://[CLOUD_RUN_URL]/docs`

**Features:**
- **Separated Architecture**: Independent frontend and backend scaling
- **Auto-scaling**: Backend scales 0-10 instances based on traffic
- **Database Sync**: SQLite automatically synced with Cloud Storage
- **CORS Configured**: Frontend can securely call HTTPS API
- **Pay-per-use**: Only pay when processing requests (scales to zero)
- **Global CDN**: Load Balancer provides edge caching for frontend

**Destroy Infrastructure:**
```bash
cd terraform
terraform destroy
```

📖 **[Complete Deployment Guide](./DEPLOYMENT.md)** - Detailed instructions, troubleshooting, and advanced configuration

### Environment Variables
```bash
DATABASE_URL=sqlite:///./risk_register.db
ALLOWED_ORIGINS=["https://your-domain.com"]
GCP_PROJECT_ID=your-project-id
GCP_BUCKET_NAME=your-bucket-name
ENVIRONMENT=prod
```

## Contributing

1. Follow the existing code style (Black + Ruff)
2. Ensure all tests pass with >90% coverage
3. Update documentation for new features
4. Use conventional commit messages
