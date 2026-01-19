from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from services.api.models import Base, Article, Entity, ArticleEntity
from services.api.schemas import ArticleResponse, SearchRequest
from sqlalchemy import create_engine, or_, text
from sqlalchemy.orm import sessionmaker, joinedload
import os
from typing import List, Optional
from libs.embeddings.embedder import generate_embedding
from libs.utils.config import get_database_url

# Database Setup
DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"sslmode": "prefer"} if "localhost" not in DATABASE_URL and "postgres:5432" not in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tables are created in the startup event below for better error handling
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="BCIIP API")

# CORS Configuration
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_db_check():
    import time
    retry_count = 5
    while retry_count > 0:
        try:
            print(f"Checking database connection... (Retries left: {retry_count})")
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                # Ensure pgvector extension is enabled
                print("Ensuring pgvector extension is active...")
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            print("Database connection established and extension ensured.")
            Base.metadata.create_all(bind=engine)
            return
        except Exception as e:
            print(f"Database connection failed: {e}")
            retry_count -= 1
            time.sleep(2)
    print("Could not connect to database after multiple retries.")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "BCIIP API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/status")
def get_status(db: Session = Depends(get_db)):
    import redis
    import datetime
    
    from libs.utils.config import get_redis_url
    
    # Redis for crawler status
    REDIS_URL = get_redis_url()
    try:
        r = redis.from_url(REDIS_URL)
        crawler_status = r.get("bciip:crawler_status")
        crawler_status = crawler_status.decode("utf-8") if crawler_status else "idle"
    except:
        crawler_status = "unknown"
        
    # DB for counts
    article_count = db.query(Article).count()
    
    return {
        "status": crawler_status,
        "article_count": article_count,
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Detailed statistics about articles and processing"""
    from sqlalchemy import func, case
    
    total_articles = db.query(Article).count()
    
    # Count by processing stage
    with_cleaned_text = db.query(Article).filter(Article.cleaned_text.isnot(None)).count()
    with_language = db.query(Article).filter(Article.language.isnot(None)).count()
    with_category = db.query(Article).filter(Article.primary_category.isnot(None)).count()
    with_summary = db.query(Article).filter(Article.summary_text.isnot(None)).count()
    with_embedding = db.query(Article).filter(Article.embedding.isnot(None)).count()
    
    # Count by source
    sources = db.query(
        Article.source,
        func.count(Article.id).label('count')
    ).group_by(Article.source).all()
    
    source_stats = {s[0]: s[1] for s in sources}
    
    # Count by category
    categories = db.query(
        Article.primary_category,
        func.count(Article.id).label('count')
    ).filter(Article.primary_category.isnot(None)).group_by(Article.primary_category).all()
    
    category_stats = {c[0]: c[1] for c in categories}
    
    return {
        "total_articles": total_articles,
        "processing_stages": {
            "acquired": total_articles,
            "cleaned": with_cleaned_text,
            "language_detected": with_language,
            "categorized": with_category,
            "summarized": with_summary,
            "embedded": with_embedding,
        },
        "by_source": source_stats,
        "by_category": category_stats,
    }

@app.get("/articles", response_model=List[ArticleResponse])
def get_articles(
    skip: int = 0, 
    limit: int = 20, 
    pub_date_from: Optional[str] = None,
    pub_date_to: Optional[str] = None,
    acq_date_from: Optional[str] = None,
    acq_date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Article).options(joinedload(Article.entities))
    
    # Filter by published date
    if pub_date_from:
        from datetime import datetime
        query = query.filter(Article.published_at >= datetime.fromisoformat(pub_date_from))
    if pub_date_to:
        from datetime import datetime
        query = query.filter(Article.published_at <= datetime.fromisoformat(pub_date_to))
    
    # Filter by acquisition date (created_at)
    if acq_date_from:
        from datetime import datetime
        query = query.filter(Article.created_at >= datetime.fromisoformat(acq_date_from))
    if acq_date_to:
        from datetime import datetime
        query = query.filter(Article.created_at <= datetime.fromisoformat(acq_date_to))
    
    articles = query.order_by(Article.published_at.desc()).offset(skip).limit(limit).all()
    return articles

@app.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: str, db: Session = Depends(get_db)):
    article = db.query(Article).options(joinedload(Article.entities)).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@app.get("/topics/{topic_name}", response_model=List[ArticleResponse])
def get_articles_by_topic(topic_name: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    articles = db.query(Article).options(joinedload(Article.entities)).filter(Article.primary_category.ilike(topic_name))\
                 .order_by(Article.published_at.desc()).offset(skip).limit(limit).all()
    return articles

@app.get("/entities/{entity_name}", response_model=List[ArticleResponse])
def get_articles_by_entity(entity_name: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    # Join Article -> ArticleEntity -> Entity
    results = db.query(Article).options(joinedload(Article.entities)).join(ArticleEntity).join(Entity)\
                .filter(Entity.text.ilike(f"%{entity_name}%"))\
                .order_by(Article.published_at.desc())\
                .offset(skip).limit(limit).all()
    return results

@app.get("/search", response_model=List[ArticleResponse])
def search_articles(q: str, type: str = "text", limit: int = 10, db: Session = Depends(get_db)):
    if type == "semantic":
        # Vector search
        query_vec = generate_embedding(q)
        if not query_vec:
            raise HTTPException(status_code=500, detail="Embedding generation failed")
            
        try:
             results = db.query(Article).order_by(Article.embedding.cosine_distance(query_vec)).limit(limit).all()
             return results
        except Exception as e:
            print(f"Vector search error: {e}")
            raise HTTPException(status_code=500, detail="Vector search failed")
    else:
        # Simple text search
        # Using ilike on multiple fields
        results = db.query(Article).options(joinedload(Article.entities)).filter(
            or_(
                Article.title.ilike(f"%{q}%"),
                Article.summary_text.ilike(f"%{q}%"),
                Article.cleaned_text.ilike(f"%{q}%")
            )
        ).limit(limit).all()
        return results
