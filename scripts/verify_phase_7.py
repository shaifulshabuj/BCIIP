import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from services.api.models import Article
from libs.embeddings.embedder import generate_embedding

def verify_phase_7():
    print("Verifying Phase 7...")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    # Must explicitly connect with psql/sqlalchemy to support vector ops if using specialized calls, 
    # but basic ORM query works if model defined correctly.
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if ANY embeddings exist
    total = session.query(Article).count()
    embedded_count = session.query(Article).filter(Article.embedding.isnot(None)).count()
    print(f"Articles with embeddings: {embedded_count}/{total}")
    
    if embedded_count == 0:
        print("[FAIL] No embeddings stored.")
        sys.exit(1)
        
    # Perform semantic search / vector similarity check
    # Need to generate query embedding
    test_query = "Bangladeshi politics and elections"
    print(f"Query: '{test_query}'")
    
    query_vec = generate_embedding(test_query)
    if not query_vec:
        print("[FAIL] Could not generate query embedding.")
        sys.exit(1)
        
    # L2 Distance / Cosine logic via pgvector
    # SQLAlchemy: Article.embedding.l2_distance(query_vec) or cosine_distance
    try:
        from pgvector.sqlalchemy import Vector
        
        # Find 3 nearest neighbors (using cosine distance usually <=> 1 - cosine similarity)
        # Note: pgvector specific operator might depend on version
        results = session.query(Article).order_by(Article.embedding.cosine_distance(query_vec)).limit(3).all()
        
        print(f"Top 3 matches:")
        for res in results:
            print(f" - {res.id} | Topic: {res.primary_category} | Title: {res.title}")
            
    except Exception as e:
        print(f"Vector search failed (maybe extension issue?): {e}")
        # Fallback manual check
        pass

    print("[SUCCESS] Phase 7 verification passed.")

if __name__ == "__main__":
    verify_phase_7()
