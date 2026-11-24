import logging
from typing import Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import mongomock

from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDBManager:
    """
    MongoDB Connection Manager.
    - Connects to real MongoDB via settings.MONGODB_URL if available.
    - Falls back to in-memory mongomock if local MongoDB is not running,
      ensuring zero crashes and seamless local testing & development.
    """
    _client: Optional[Any] = None
    _db: Optional[Any] = None
    _is_mock: bool = False

    @classmethod
    def get_database(cls):
        if cls._db is not None:
            return cls._db

        url = settings.MONGODB_URL
        db_name = settings.MONGODB_DB_NAME

        try:
            logger.info(f"Connecting to MongoDB at {url}...")
            # Short timeout to detect if local mongod is active without stalling
            real_client = MongoClient(url, serverSelectionTimeoutMS=1500)
            real_client.admin.command("ping")
            cls._client = real_client
            cls._db = cls._client[db_name]
            cls._is_mock = False
            logger.info(f"Successfully connected to MongoDB database '{db_name}'.")
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            logger.warning(
                f"Could not connect to external MongoDB ({e}). "
                f"Initializing resilient in-memory MongoDB engine (mongomock) for '{db_name}'."
            )
            cls._client = mongomock.MongoClient()
            cls._db = cls._client[db_name]
            cls._is_mock = True

        # Initialize collections & indexes
        cls._init_indexes(cls._db)
        return cls._db

    @classmethod
    def _init_indexes(cls, db):
        try:
            # Users unique email index
            db.users.create_index("email", unique=True)
            # Resumes user_id index
            db.resumes.create_index("user_id")
            # Jobs user_id index
            db.jobs.create_index("user_id")
            # Analyses user_id index
            db.analyses.create_index("user_id")
        except Exception as e:
            logger.debug(f"Index creation note: {e}")

    @classmethod
    def is_mock(cls) -> bool:
        return cls._is_mock

    @classmethod
    def close(cls):
        if cls._client:
            try:
                cls._client.close()
            except Exception:
                pass
            cls._client = None
            cls._db = None

def get_database():
    """Dependency helper to get the database instance."""
    return MongoDBManager.get_database()

