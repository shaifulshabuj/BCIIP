import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.models import Article
from minio import Minio

def verify_phase_1():
    print("Verifying Phase 1...")
    
    # DB Connection
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 1. Check Article Count
    count = session.query(Article).count()
    print(f"Article count in DB: {count}")
    
    if count == 0:
        print("[FAIL] No articles found in database.")
        sys.exit(1)
        
    # 2. Check MinIO Content
    article = session.query(Article).first()
    path = article.raw_storage_path
    print(f"Checking MinIO object: {path}")
    
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"
    MINIO_BUCKET = "articles-raw"
    
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )
    
    try:
        data = client.get_object(MINIO_BUCKET, path)
        content = data.read()
        print(f"Retrieved {len(content)} bytes from MinIO.")
        if len(content) == 0:
            print("[FAIL] Empty content in MinIO.")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Could not retrieve object from MinIO: {e}")
        sys.exit(1)
        
    print("[SUCCESS] Phase 1 verification passed.")

if __name__ == "__main__":
    verify_phase_1()
