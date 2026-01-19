import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from minio import Minio
from services.api.models import Article
from libs.text_cleaning.cleaner import clean_html, extract_from_pdf
from libs.language_detection.detector import detect_language
from libs.categorization.categorizer import categorize_text
from libs.entity_extraction.extractor import extract_entities
from libs.summarization.summarizer import generate_summary
from libs.embeddings.embedder import generate_embedding
from services.api.models import Article, Entity, ArticleEntity
from sqlalchemy.dialects.postgresql import insert

# Config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/bciip")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"
MINIO_BUCKET = "articles-raw"

# Setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def run_process():
    print("Starting Processor Service...")
    session = SessionLocal()
    
    # Fetch articles that need cleaning (raw_path exists, cleaned_text is null)
    # Limit batch size to avoid memory issues (e.g., 50 at a time)
    # Also process articles that have cleaned_text but NO language (for backfill)
    articles = session.query(Article).filter(
        Article.raw_storage_path.isnot(None)
    ).limit(50).all()
    # Simplified filter: just fetch 50 and check logic in list iteration to see what needs work
    # Or keep specific filter? using simple filter to catch partials.
    # Refined filter:
    articles = session.query(Article).filter(
        Article.raw_storage_path.isnot(None), 
        # Only process if embedding is missing (last step)
        Article.embedding.is_(None)
    ).limit(50).all()
    
    print(f"Found {len(articles)} articles to process.")
    
    for article in articles:
        try:
            # Phase 2: Cleaning
            cleaned_text = article.cleaned_text
            word_count = article.word_count
            
            if not cleaned_text:
                # Get from MinIO
                try:
                    data = minio_client.get_object(MINIO_BUCKET, article.raw_storage_path)
                    content_bytes = data.read()
                    
                    if article.raw_storage_path.endswith('.pdf'):
                        cleaned_text = extract_from_pdf(content_bytes)
                    else:
                        # Default to HTML
                        cleaned_text = clean_html(content_bytes.decode('utf-8', errors='ignore'))
                    
                    word_count = len(cleaned_text.split()) if cleaned_text else 0
                    
                    article.cleaned_text = cleaned_text
                    article.word_count = str(word_count) 
                except Exception as e:
                    print(f"MinIO/Cleaning error for {article.id}: {e}")
                    # If MinIO fails, we can't do much. 
                    continue

            if not cleaned_text:
                continue

            # Phase 3: Language Detection
            lang = article.language
            if not lang:
                lang, conf = detect_language(cleaned_text)
                article.language = lang
                article.language_confidence = str(conf)
            
            # Phase 4: Categorization
            topic = article.primary_category
            if not topic:
                topic, topic_conf = categorize_text(cleaned_text, lang)
                article.primary_category = topic
                article.topic_confidence = str(topic_conf)
            
            # Phase 5: Entity Extraction
            # Check if we already have entities linked? 
            # We can check DB, but extraction is fast enough to redo for safety
            entities = extract_entities(cleaned_text, lang)
            for ent_type, ent_text in entities:
                # Get or create Entity
                existing_ent = session.query(Entity).filter_by(text=ent_text, type=ent_type).first()
                if not existing_ent:
                    existing_ent = Entity(text=ent_text, type=ent_type)
                    session.add(existing_ent)
                    session.flush() # Get ID
                
                # Check link
                existing_link = session.query(ArticleEntity).filter_by(article_id=article.id, entity_id=existing_ent.id).first()
                if not existing_link:
                    link = ArticleEntity(article_id=article.id, entity_id=existing_ent.id)
                    session.add(link)

            # Phase 6: Summarization
            summary_text = article.summary_text
            if not summary_text:
                summary_text, summary_bullets = generate_summary(cleaned_text, lang)
                if summary_text:
                    article.summary_text = summary_text
                    article.summary_bullets = summary_bullets
                
            # Phase 7: Embeddings
            if not article.embedding:
                text_to_embed = summary_text if summary_text else (cleaned_text[:500] if cleaned_text else "")
                embedding = generate_embedding(text_to_embed)
                if embedding:
                    article.embedding = embedding
            
            print(f"Processed {article.id}: {word_count} words., Lang: {lang}, Topic: {topic}, Entities: {len(entities)}, Summary: {'Yes' if summary_text else 'No'}, Embed: {'Yes' if embedding else 'No'}")
            
            # Commit per article or batch? Per article safer for job retry.
            session.commit()
            
        except Exception as e:
            print(f"Error processing article {article.id}: {e}")
            session.rollback()
            # Continue to next article
            pass
            
    print("Batch complete.")
    session.close()

if __name__ == "__main__":
    run_process()
