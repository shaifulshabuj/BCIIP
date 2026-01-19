import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.models import Article

def verify_phase_6():
    print("Verifying Phase 6...")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    total = session.query(Article).count()
    if total == 0:
        print("[FAIL] No articles in DB.")
        sys.exit(1)
        
    summary_count = session.query(Article).filter(Article.summary_text.isnot(None)).count()
    print(f"Articles with summary: {summary_count}/{total}")
    
    if summary_count == 0:
         print("[FAIL] No summaries generated.")
         sys.exit(1)
    
    # Dump sample
    sample = session.query(Article).filter(Article.summary_text.isnot(None)).first()
    print(f"Sample ({sample.id}):")
    print(f"Summary (len={len(sample.summary_text)}): {sample.summary_text[:100]}...")
    print(f"Bullets:\n{sample.summary_bullets}")
    
    print("[SUCCESS] Phase 6 verification passed.")

if __name__ == "__main__":
    verify_phase_6()
