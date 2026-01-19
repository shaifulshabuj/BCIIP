import os
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """
    Centralized utility to discover and normalize the database URL.
    Checks multiple environment variables and fixes the SQLAlchemy scheme.
    """
    # Priority 1: DATABASE_URL (Standard)
    # Priority 2: POSTGRES_URL (Common in Railway)
    db_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    
    # Fallback to local development postgres if nothing is set
    if not db_url:
        db_url = "postgresql://user:password@postgres:5432/bciip"
        logger.info("Using default local database URL fallback.")
    
    # Normalize postgres:// to postgresql:// for SQLAlchemy 1.4+
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    try:
        parsed = urlparse(db_url)
        # Safe logging: show host and db name only
        logger.info(f"Database target: {parsed.hostname}:{parsed.port or 5432} (DB: {parsed.path.lstrip('/')})")
    except Exception as e:
        logger.warning(f"Could not parse database URL for diagnostic logging: {e}")
        
    return db_url
