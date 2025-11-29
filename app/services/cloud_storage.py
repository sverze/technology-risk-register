"""Cloud Storage service for managing SQLite database sync."""

import logging
from pathlib import Path

from google.cloud import storage

from app.core.config import settings

logger = logging.getLogger(__name__)


class CloudStorageService:
    """Service for managing database files in Google Cloud Storage."""

    def __init__(self):
        self.client: storage.Client | None = None
        self.bucket_name = settings.GCP_BUCKET_NAME
        self.project_id = settings.GCP_PROJECT_ID
        self.db_filename = "risk_register.db"
        self.local_db_path = Path("./risk_register.db")

    def _get_client(self) -> storage.Client:
        """Get or create Google Cloud Storage client."""
        if self.client is None:
            if self.project_id:
                self.client = storage.Client(project=self.project_id)
            else:
                # For local development or when running outside GCP
                self.client = storage.Client()
        return self.client

    def _get_bucket(self) -> storage.Bucket | None:
        """Get the Cloud Storage bucket."""
        if not self.bucket_name:
            logger.warning("GCP_BUCKET_NAME not configured, skipping Cloud Storage operations")
            return None

        try:
            client = self._get_client()
            return client.bucket(self.bucket_name)
        except Exception as e:
            logger.error(f"Failed to get bucket {self.bucket_name}: {e}")
            return None

    def download_database(self) -> bool:
        """Download database from Cloud Storage to local file."""
        if not self._should_use_cloud_storage():
            return False

        bucket = self._get_bucket()
        if not bucket:
            return False

        try:
            blob = bucket.blob(self.db_filename)

            # Check if file exists in Cloud Storage
            if not blob.exists():
                logger.info(f"Database file {self.db_filename} not found in Cloud Storage, will create new one")
                return False

            # Download the file
            blob.download_to_filename(str(self.local_db_path))
            logger.info("Successfully downloaded database from Cloud Storage")
            return True

        except Exception as e:
            logger.error(f"Failed to download database from Cloud Storage: {e}")
            return False

    def upload_database(self) -> bool:
        """Upload local database file to Cloud Storage."""
        if not self._should_use_cloud_storage():
            return False

        if not self.local_db_path.exists():
            logger.warning(f"Local database file {self.local_db_path} does not exist")
            return False

        bucket = self._get_bucket()
        if not bucket:
            return False

        try:
            blob = bucket.blob(self.db_filename)
            blob.upload_from_filename(str(self.local_db_path))
            logger.info("Successfully uploaded database to Cloud Storage")
            return True

        except Exception as e:
            logger.error(f"Failed to upload database to Cloud Storage: {e}")
            return False

    def sync_database_from_cloud(self, timeout_seconds: int = 30) -> bool:
        """Sync database from Cloud Storage if it's newer or local doesn't exist."""
        if not self._should_use_cloud_storage():
            logger.info("Cloud Storage not configured, skipping sync")
            return False

        logger.info(f"Starting Cloud Storage sync with {timeout_seconds}s timeout")

        try:
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"Cloud Storage sync timed out after {timeout_seconds}s")

            # Set timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)

            bucket = self._get_bucket()
            if not bucket:
                logger.warning("Could not get Cloud Storage bucket")
                return False

            blob = bucket.blob(self.db_filename)

            if not blob.exists():
                logger.info("No database found in Cloud Storage")
                return False

            # If local file doesn't exist, download it
            if not self.local_db_path.exists():
                logger.info("Local database doesn't exist, downloading from Cloud Storage")
                result = self.download_database()
                signal.alarm(0)  # Cancel timeout
                return result

            # Compare modification times
            blob.reload()  # Refresh blob metadata
            local_mtime = self.local_db_path.stat().st_mtime
            cloud_mtime = blob.updated.timestamp()

            if cloud_mtime > local_mtime:
                logger.info("Cloud database is newer, downloading")
                result = self.download_database()
                signal.alarm(0)  # Cancel timeout
                return result
            else:
                logger.info("Local database is up to date")
                signal.alarm(0)  # Cancel timeout
                return True

        except TimeoutError as e:
            logger.warning(f"Cloud Storage sync timed out: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to sync database from Cloud Storage: {e}")
            return False
        finally:
            signal.alarm(0)  # Ensure timeout is canceled

    def _should_use_cloud_storage(self) -> bool:
        """Check if Cloud Storage should be used."""
        return bool(self.bucket_name and self.project_id)


# Global instance
cloud_storage_service = CloudStorageService()
