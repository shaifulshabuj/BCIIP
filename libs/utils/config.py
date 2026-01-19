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

def get_redis_url():
    """
    Centralized utility to discover the Redis URL.
    Checks for REDIS_URL or builds it from individual variables.
    """
    redis_url = os.getenv("REDIS_URL")
    
    if not redis_url:
        rhost = os.getenv("REDISHOST")
        rport = os.getenv("REDISPORT", "6379")
        ruser = os.getenv("REDISUSER", "")
        rpass = os.getenv("REDISPASSWORD", "")
        
        if rhost:
            auth = f"{ruser}:{rpass}@" if rpass else ""
            redis_url = f"redis://{auth}{rhost}:{rport}/0"
            logger.info(f"Building REDIS_URL from individual variables.")
    
    if not redis_url:
        redis_url = "redis://redis:6379/0"
        logger.info("Using default local Redis URL fallback.")
        
    try:
        parsed = urlparse(redis_url)
        logger.info(f"Redis target: {parsed.hostname}:{parsed.port or 6379}")
    except Exception as e:
        logger.warning(f"Could not parse Redis URL for diagnostic logging: {e}")
        
    return redis_url

def get_minio_config():
    """
    Centralized utility to discover MinIO configuration.
    Automatically handles internal vs external networking.
    """
    endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    
    # Strip protocol if provided (Minio client expects host:port)
    if "://" in endpoint:
        endpoint = endpoint.split("://")[1]
        
    is_internal = ".railway.internal" in endpoint or endpoint.startswith("minio")
    
    # Secure: default to false for internal, detect for external
    secure_env = os.getenv("MINIO_SECURE")
    if secure_env is not None:
        secure = secure_env.lower() == "true"
    else:
        # Default to false for internal addresses, true for external public URLs
        secure = not is_internal

    # Default Port: If no port is specified, use 9000 for internal
    if ":" not in endpoint and is_internal:
        endpoint = f"{endpoint}:9000"

    logger.info(f"MinIO target: {endpoint} (Secure: {secure})")
    
    return {
        "endpoint": endpoint,
        "access_key": os.getenv("MINIO_ACCESS_KEY", os.getenv("MINIO_ROOT_USER", "minioadmin")),
        "secret_key": os.getenv("MINIO_SECRET_KEY", os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")),
        "secure": secure
    }
