"""Admin API endpoints for maintenance operations."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.cloud_storage import cloud_storage_service

router = APIRouter()


@router.post("/sync-database")
def sync_database_to_cloud() -> Dict[str, str]:
    """Manually sync database to Cloud Storage."""
    try:
        success = cloud_storage_service.upload_database()
        if success:
            return {"status": "success", "message": "Database synced to Cloud Storage"}
        else:
            return {"status": "skipped", "message": "Cloud Storage not configured or sync skipped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync database: {str(e)}")


@router.post("/download-database")
def download_database_from_cloud() -> Dict[str, str]:
    """Manually download database from Cloud Storage."""
    try:
        success = cloud_storage_service.download_database()
        if success:
            return {"status": "success", "message": "Database downloaded from Cloud Storage"}
        else:
            return {"status": "skipped", "message": "Cloud Storage not configured or no database found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download database: {str(e)}")


@router.get("/cloud-storage-status")
def get_cloud_storage_status() -> Dict[str, Any]:
    """Get Cloud Storage configuration status."""
    return {
        "bucket_name": cloud_storage_service.bucket_name,
        "project_id": cloud_storage_service.project_id,
        "configured": cloud_storage_service._should_use_cloud_storage(),
        "local_db_exists": cloud_storage_service.local_db_path.exists()
    }