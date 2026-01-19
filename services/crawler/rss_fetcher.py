import feedparser
import requests
import uuid
import os
import io
from datetime import datetime
from minio import Minio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from libs.utils.config import get_database_url, get_redis_url, get_minio_config
from services.api.models import Article, Base

# Configuration
DATABASE_URL = get_database_url()
MINIO_CONFIG = get_minio_config()
MINIO_ENDPOINT = MINIO_CONFIG["endpoint"]
MINIO_ACCESS_KEY = MINIO_CONFIG["access_key"]
MINIO_SECRET_KEY = MINIO_CONFIG["secret_key"]
MINIO_BUCKET = "articles-raw"
MINIO_SECURE = MINIO_CONFIG["secure"]

# MinIO Setup
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)

# DB Setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure tables exist (Simple MVP approach)
Base.metadata.create_all(bind=engine)

def fetch_and_process_feed(source_name, rss_url):
    print(f"Fetching {source_name} from {rss_url}...")
    feed = feedparser.parse(rss_url)
    
    session = SessionLocal()
    count = 0
    
    for entry in feed.entries:
        try:
            url = entry.link
            
            # Check for existing
            existing = session.query(Article).filter(Article.url == url).first()
            if existing:
                continue
                
            title = entry.title
            published_parsed = entry.get("published_parsed")
            published_at = datetime.fromtimestamp(time.mktime(published_parsed)) if published_parsed else datetime.utcnow()
            
            # Download Raw Content
            # For some RSS, the content is in the feed, but specs say "Store raw HTML/text".
            # Usually implies visiting the page.
            try:
                resp = requests.get(url, timeout=10)
                raw_html = resp.content
            except Exception as e:
                print(f"Failed to fetch content for {url}: {e}")
                continue

            # Upload to MinIO
            object_name = f"{source_name}/{uuid.uuid4()}.html"
            minio_client.put_object(
                MINIO_BUCKET,
                object_name,
                io.BytesIO(raw_html),
                len(raw_html),
                content_type="text/html"
            )

            # Save to DB
            article = Article(
                url=url,
                source=source_name,
                title=title,
                published_at=published_at,
                raw_storage_path=object_name
            )
            session.add(article)
            count += 1
            
        except Exception as e:
            print(f"Error processing entry {entry.get('link', 'unknown')}: {e}")
            continue
    
    session.commit()
    session.close()
    print(f"Imported {count} new articles from {source_name}")

import time
