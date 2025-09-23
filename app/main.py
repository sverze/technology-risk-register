from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import settings
from app.core.database import create_tables, get_db
from app.core.seed_data import seed_dropdown_values
from app.services.cloud_storage import cloud_storage_service

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Technology Risk Register API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    import logging

    logger = logging.getLogger(__name__)

    logger.info("Starting application startup...")

    # Download database from Cloud Storage if available (with short timeout)
    try:
        logger.info("Attempting Cloud Storage sync...")
        cloud_storage_service.sync_database_from_cloud(timeout_seconds=15)
    except Exception as e:
        logger.warning(f"Cloud Storage sync failed, continuing with local database: {e}")

    logger.info("Creating database tables...")
    create_tables()

    # Seed dropdown values and sample risks
    logger.info("Seeding database...")
    db = next(get_db())
    try:
        seed_dropdown_values(db)
        # Temporarily skip sample risk seeding to fix startup issue
        # seed_sample_risks(db)
        logger.info("Database seeding completed (risk log entries skipped for debugging)")

        # Upload database to Cloud Storage after seeding (if needed)
        try:
            cloud_storage_service.upload_database()
            logger.info("Database uploaded to Cloud Storage")
        except Exception as e:
            logger.warning(f"Failed to upload database to Cloud Storage: {e}")
    finally:
        db.close()

    logger.info("Application startup completed successfully")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Technology Risk Register API"}


@app.on_event("shutdown")
def shutdown_event():
    """Shutdown cleanup - database persisted via Cloud Storage mount."""
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Application shutdown - uploading database to Cloud Storage")
    try:
        cloud_storage_service.upload_database()
    except Exception as e:
        logger.warning(f"Failed to upload database on shutdown: {e}")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
