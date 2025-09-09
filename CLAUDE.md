# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Technology Risk Register Application

This is a web application for managing technology risks with a dashboard view and tabular entries view. Built with FastAPI backend, React frontend, and SQLite database that deploys serverlessly to GCP.

## Development Commands

### Backend Development
```bash
# Run the development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

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
# Start local development environment
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop and clean up
docker-compose down -v
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
- Local: SQLite database file
- GCP: Cloud Run + SQLite file in Cloud Storage
- Database migrations run automatically on startup
- Environment variables for configuration
