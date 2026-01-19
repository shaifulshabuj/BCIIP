from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from services.api.models import Base, Article, Entity, ArticleEntity
from services.api.schemas import ArticleResponse, SearchRequest
from sqlalchemy import create_engine, or_, text
from sqlalchemy.orm import sessionmaker
import os
from typing import List
from libs.embeddings.embedder import generate_embedding

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/bciip")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables (if not handled by migration scripts, good for safety)
# For pgvector type, we might need to assume extension is active.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BCIIP API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "BCIIP API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/articles", response_model=List[ArticleResponse])
def get_articles(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    articles = db.query(Article).order_by(Article.published_at.desc()).offset(skip).limit(limit).all()
    # Simple list view, usually we'd load entities via relationship or separate query.
    # For now, to match schema, we return them. If entities missing, Pydantic defaults to empty list.
    return articles

@app.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: str, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    # Manual fetch of entities since we didn't add relationship to model properly for ORM
    links = db.query(ArticleEntity).filter(ArticleEntity.article_id == article.id).all()
    entities = []
    for link in links:
        ent = db.query(Entity).get(link.entity_id)
        if ent:
            entities.append(ent)
            
    # Hack to attach entities for Pydantic serialization
    article.entities = entities 
    return article

@app.get("/topics/{topic_name}", response_model=List[ArticleResponse])
def get_articles_by_topic(topic_name: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    articles = db.query(Article).filter(Article.primary_category.ilike(topic_name))\
                 .order_by(Article.published_at.desc()).offset(skip).limit(limit).all()
    return articles

@app.get("/entities/{entity_name}", response_model=List[ArticleResponse])
def get_articles_by_entity(entity_name: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    # Join Article -> ArticleEntity -> Entity
    results = db.query(Article).join(ArticleEntity).join(Entity)\
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
        results = db.query(Article).filter(
            or_(
                Article.title.ilike(f"%{q}%"),
                Article.summary_text.ilike(f"%{q}%"),
                Article.cleaned_text.ilike(f"%{q}%")
            )
        ).limit(limit).all()
        return results
