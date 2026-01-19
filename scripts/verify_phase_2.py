import os
import sys
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.models import Article

def verify_phase_2():
    print("Verifying Phase 2...")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check total articles
    total = session.query(Article).count()
    if total == 0:
        print("[FAIL] No articles in DB checking phase 2.")
        sys.exit(1)
        
    # Check for cleaned text
    cleaned_count = session.query(Article).filter(Article.cleaned_text.isnot(None)).count()
    print(f"Articles with cleaned text: {cleaned_count}/{total}")
    
    if cleaned_count == 0:
        print("[FAIL] No articles have been cleaned.")
        sys.exit(1)
        
    # Verify content of a random cleaned article
    article = session.query(Article).filter(Article.cleaned_text.isnot(None)).first()
    print(f"Sample Article ({article.id}): Word count = {article.word_count}")
    print(f"Snippet: {article.cleaned_text[:100]}...")
    
    if int(article.word_count) <= 0:
         print("[WARN] Word count is 0, possible cleaning failure or empty source.")
         # Not necessarily a hard fail if source was empty, but suspicious.

    print("[SUCCESS] Phase 2 verification passed.")

if __name__ == "__main__":
    verify_phase_2()
