import os
import sys
import redis
import psycopg2
from minio import Minio
from minio.error import S3Error

def verify_postgres():
    try:
        url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        print("[OK] PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"[FAIL] PostgreSQL connection failed: {e}")
        return False

def verify_redis():
    try:
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(url)
        r.ping()
        print("[OK] Redis connection successful")
        return True
    except Exception as e:
        print(f"[FAIL] Redis connection failed: {e}")
        return False

def verify_minio():
    try:
        endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        secure = os.getenv("MINIO_SECURE", "False").lower() == "true"
        
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        
        # List buckets to verify auth and connection
        client.list_buckets()
        print("[OK] MinIO connection successful")
        return True
    except Exception as e:
        print(f"[FAIL] MinIO connection failed: {e}")
        return False

def main():
    print("Verifying Phase 0 Connectivity...")
    pg_ok = verify_postgres()
    redis_ok = verify_redis()
    minio_ok = verify_minio()
    
    if pg_ok and redis_ok and minio_ok:
        print("\n[SUCCESS] All Phase 0 checks passed!")
        sys.exit(0)
    else:
        print("\n[FAILURE] One or more checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
