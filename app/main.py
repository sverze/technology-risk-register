from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import settings
from app.core.database import create_tables, get_db
from app.core.seed_data import seed_dropdown_values

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
    create_tables()
    # Seed dropdown values
    db = next(get_db())
    try:
        seed_dropdown_values(db)
    finally:
        db.close()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Technology Risk Register API"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}
