import requests
import os
import sys
import time
from sqlalchemy import create_engine, text
from minio import Minio

# Config
API_URL = "http://localhost:8000"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/bciip")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

def check_component(name, func):
    try:
        print(f"Checking {name}...", end=" ")
        func()
        print("[OK]")
        return True
    except Exception as e:
        print(f"[FAIL] - {e}")
        return False

def check_api():
    r = requests.get(f"{API_URL}/health", timeout=5)
    r.raise_for_status()

def check_db():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

def check_minio():
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )
    client.list_buckets()

def check_data_integrity():
    # Check if we have articles with all phases complete
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check total articles
        count = conn.execute(text("SELECT COUNT(*) FROM articles")).scalar()
        print(f"\n   Total Articles: {count}")
        
        # Check vector embeddings
        embed_count = conn.execute(text("SELECT COUNT(*) FROM articles WHERE embedding IS NOT NULL")).scalar()
        print(f"   Articles with Embeddings: {embed_count}")

        if count == 0:
             raise Exception("No articles found in DB.")
        if embed_count == 0:
             raise Exception("No embeddings found (Pipeline Phase 7 issue).")

def verify_all():
    print("=== BCIIP Full System Verification ===\n")
    
    components = [
        ("API Health", check_api),
        ("Database Connection", check_db),
        ("MinIO Connection", check_minio),
        ("Data Consistency", check_data_integrity)
    ]
    
    failures = 0
    for name, func in components:
        if not check_component(name, func):
            failures += 1
            
    print("\n========================================")
    if failures == 0:
        print("RESULT: SYSTEM HEALTHY [SUCCESS]")
        sys.exit(0)
    else:
        print(f"RESULT: {failures} CHECKS FAILED [FAILURE]")
        sys.exit(1)

if __name__ == "__main__":
    verify_all()
