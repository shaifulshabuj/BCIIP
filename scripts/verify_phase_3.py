import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.models import Article

def verify_phase_3():
    print("Verifying Phase 3...")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check total articles
    total = session.query(Article).count()
    if total == 0:
        print("[FAIL] No articles in DB checking phase 3.")
        sys.exit(1)
        
    # Check for language
    lang_count = session.query(Article).filter(Article.language.isnot(None)).count()
    print(f"Articles with language detected: {lang_count}/{total}")
    
    if lang_count == 0:
        print("[FAIL] No articles have language detected.")
        sys.exit(1)
        
    # Check specific examples (Prothom Alo should be 'bn', Daily Star often 'en' but sometimes 'bn')
    bn_count = session.query(Article).filter(Article.language == 'bn').count()
    en_count = session.query(Article).filter(Article.language == 'en').count()
    
    print(f"Bangla articles: {bn_count}")
    print(f"English articles: {en_count}")
    
    if bn_count == 0 and en_count == 0:
         print("[WARN] All languages are 'other'?")
    
    # Dump a sample
    sample = session.query(Article).filter(Article.language.isnot(None)).first()
    print(f"Sample ({sample.id}): Lang={sample.language} Conf={sample.language_confidence}")

    print("[SUCCESS] Phase 3 verification passed.")

if __name__ == "__main__":
    verify_phase_3()
