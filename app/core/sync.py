"""Database synchronization decorator for Cloud Storage persistence."""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from app.services.cloud_storage import cloud_storage_service

logger = logging.getLogger(__name__)


def sync_database_after_write(func: Callable) -> Callable:
    """
    Decorator that automatically uploads the database to Cloud Storage
    after successful database write operations.

    Use this decorator on service methods that modify the database
    to ensure data persistence in Cloud Run environments.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Execute the original function
        result = func(*args, **kwargs)

        # If the function completed successfully, sync to cloud storage
        try:
            success = cloud_storage_service.upload_database()
            if success:
                logger.debug(f"Database synced to Cloud Storage after {func.__name__}")
            else:
                logger.debug(f"Cloud Storage sync skipped after {func.__name__} (not configured)")
        except Exception as e:
            # Log the error but don't fail the original operation
            logger.warning(f"Failed to sync database to Cloud Storage after {func.__name__}: {e}")

        return result

    return wrapper


def sync_database_after_commit(func: Callable) -> Callable:
    """
    Decorator that automatically uploads the database to Cloud Storage
    after successful database commit operations.

    This version is specifically for methods that handle their own transactions.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        result = func(*args, **kwargs)

        # Only sync if we have a result (indicating success)
        if result is not None:
            try:
                success = cloud_storage_service.upload_database()
                if success:
                    logger.debug(f"Database synced to Cloud Storage after {func.__name__}")
            except Exception as e:
                logger.warning(f"Failed to sync database to Cloud Storage after {func.__name__}: {e}")

        return result

    return wrapper
