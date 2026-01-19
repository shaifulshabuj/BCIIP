from usp.tree import sitemap_tree_for_homepage
import requests
from datetime import datetime
import uuid
import io
import os
from minio import Minio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from libs.utils.config import get_database_url, get_minio_config
from services.api.models import Article, Base

# Configuration (Reuse existing)
DATABASE_URL = get_database_url()
MINIO_CONFIG = get_minio_config()
MINIO_ENDPOINT = MINIO_CONFIG["endpoint"]
MINIO_ACCESS_KEY = MINIO_CONFIG["access_key"]
MINIO_SECRET_KEY = MINIO_CONFIG["secret_key"]
MINIO_BUCKET = "articles-raw"
MINIO_SECURE = MINIO_CONFIG["secure"]

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_resources():
    """
    Lazy initialization for network resources.
    """
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Resource initialization failed: {e}")
        raise

def fetch_sitemap(url, source_name):
    init_resources()
    print(f"Fetching sitemap for {url}...")
    tree = sitemap_tree_for_homepage(url)
    
    session = SessionLocal()
    count = 0
    limit = 50 # Validating concept only
    
    for page in tree.all_pages():
        if count >= limit:
            break
            
        try:
            article_url = page.url
            # Filter checks
            existing = session.query(Article).filter(Article.url == article_url).first()
            if existing:
                continue
                
            print(f"Backfilling: {article_url}")
            
            # Fetch content
            try:
                resp = requests.get(article_url, timeout=10)
                raw_html = resp.content
            except Exception as e:
                print(f"Failed to fetch {article_url}: {e}")
                continue

            # Upload to MinIO
            object_name = f"{source_name}/backfill/{uuid.uuid4()}.html"
            minio_client.put_object(
                MINIO_BUCKET,
                object_name,
                io.BytesIO(raw_html),
                len(raw_html),
                content_type="text/html"
            )

            # Save to DB
            # Try to infer date from URL or headers if available, else now
            published_at = datetime.now() # naive fallback
            
            article = Article(
                url=article_url,
                source=source_name,
                title=article_url, # Temporary title until processing
                published_at=published_at,
                raw_storage_path=object_name
            )
            session.add(article)
            count += 1
            
        except Exception as e:
            print(f"Error processing {page.url}: {e}")
            
    session.commit()
    session.close()
    print(f"Backfilled {count} articles for {source_name}")

if __name__ == "__main__":
    # Test
    fetch_sitemap('https://www.thedailystar.net/', 'Daily Star')
