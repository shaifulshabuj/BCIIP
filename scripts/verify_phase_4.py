import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.models import Article

def verify_phase_4():
    print("Verifying Phase 4...")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    total = session.query(Article).count()
    if total == 0:
        print("[FAIL] No articles in DB.")
        sys.exit(1)
        
    cat_count = session.query(Article).filter(Article.primary_category.isnot(None)).count()
    print(f"Categorized articles: {cat_count}/{total}")
    
    if cat_count == 0:
         print("[FAIL] No taxonomy applied.")
         sys.exit(1)
         
    # Check breakdowns
    counts = {}
    for row in session.query(Article.primary_category).all():
        topic = row[0]
        counts[topic] = counts.get(topic, 0) + 1
        
    print("Topic breakdown:", counts)
    
    # Dump sample
    sample = session.query(Article).filter(Article.primary_category.isnot(None)).first()
    print(f"Sample ({sample.id}): Topic={sample.primary_category} Conf={sample.topic_confidence}")
    
    print("[SUCCESS] Phase 4 verification passed.")

if __name__ == "__main__":
    verify_phase_4()
