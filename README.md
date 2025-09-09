# Technology Risk Register

A modern web application for managing technology risks with executive dashboard reporting, built with FastAPI backend and SQLite database optimized for serverless deployment to GCP.

## Features

- **Risk Management**: Complete CRUD operations for technology risks
- **Executive Dashboard**: Real-time metrics and visualizations for decision makers
- **Audit Trail**: Full history tracking of risk changes
- **Intelligent Prioritization**: Smart risk sorting by rating, financial impact, and business service impact
- **Serverless Ready**: SQLite + Cloud Storage architecture for cost-effective GCP deployment

## Technology Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: SQLite (local development and GCP deployment)
- **ORM**: SQLAlchemy with Alembic migrations
- **Testing**: Pytest with coverage
- **Code Quality**: Black, Ruff, MyPy, pre-commit hooks
- **Deployment**: Docker, GCP Cloud Run, Cloud Storage

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

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - API: http://localhost:8000

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
# Run all tests with coverage
uv run pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
uv run pytest tests/test_risks.py -v

# Run tests with coverage threshold
uv run pytest --cov=app --cov-fail-under=90
```

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
1. SQLite database file stored in Cloud Storage bucket
2. Cloud Run service mounts database file at startup
3. Automatic scaling based on traffic
4. Pay-per-use pricing model

### Environment Variables
```bash
DATABASE_URL=sqlite:///./risk_register.db
ALLOWED_ORIGINS=["http://localhost:3000"]
GCP_PROJECT_ID=your-project-id
GCP_BUCKET_NAME=your-bucket-name
```

## Contributing

1. Follow the existing code style (Black + Ruff)
2. Ensure all tests pass with >90% coverage
3. Update documentation for new features
4. Use conventional commit messages
