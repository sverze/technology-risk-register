"""Admin API endpoints for maintenance operations."""

import os
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.cloud_storage import cloud_storage_service

router = APIRouter()


@router.post("/sync-database")
def sync_database_to_cloud() -> dict[str, str]:
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
def download_database_from_cloud() -> dict[str, str]:
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
def get_cloud_storage_status() -> dict[str, Any]:
    """Get Cloud Storage configuration status."""
    return {
        "bucket_name": cloud_storage_service.bucket_name,
        "project_id": cloud_storage_service.project_id,
        "configured": cloud_storage_service._should_use_cloud_storage(),
        "local_db_exists": cloud_storage_service.local_db_path.exists(),
    }


@router.get("/filesystem-diagnostic")
def filesystem_diagnostic() -> dict[str, Any]:
    """Diagnose filesystem mount and database operations."""
    try:
        data_path = Path("/data")
        db_path = Path("/data/risk_register.db")

        # Check mount point
        mount_info = {
            "data_dir_exists": data_path.exists(),
            "data_dir_writable": False,
            "data_dir_contents": [],
        }

        if data_path.exists():
            try:
                # Test write permissions
                test_file = data_path / "write_test.txt"
                test_file.write_text("test")
                mount_info["data_dir_writable"] = True
                test_file.unlink()  # cleanup

                # List contents
                mount_info["data_dir_contents"] = [item.name for item in data_path.iterdir()]
            except Exception as e:
                mount_info["write_error"] = str(e)

        # Check database
        db_info = {
            "db_file_exists": db_path.exists(),
            "db_file_size": 0,
            "sqlite_connection_test": False,
            "sqlite_error": None,
        }

        if db_path.exists():
            db_info["db_file_size"] = db_path.stat().st_size

            # Test SQLite connection
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()
                db_info["sqlite_connection_test"] = True
                db_info["tables"] = tables  # type: ignore[assignment]
            except Exception as e:
                db_info["sqlite_error"] = str(e)  # type: ignore[assignment]

        # Environment info
        env_info = {
            "DATABASE_URL": os.getenv("DATABASE_URL", "Not set"),
            "GCP_BUCKET_NAME": os.getenv("GCP_BUCKET_NAME", "Not set"),
            "working_directory": str(Path.cwd()),
        }

        return {"status": "success", "mount": mount_info, "database": db_info, "environment": env_info}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnostic failed: {str(e)}")
