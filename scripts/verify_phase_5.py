import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.models import Article, Entity, ArticleEntity

def verify_phase_5():
    print("Verifying Phase 5...")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check entities count
    ent_count = session.query(Entity).count()
    print(f"Total Unique Entities: {ent_count}")
    
    if ent_count == 0:
        print("[FAIL] No entities extracted.")
        sys.exit(1)
        
    # Check associations
    link_count = session.query(ArticleEntity).count()
    print(f"Total Entity Occurrences (Links): {link_count}")
    
    if link_count == 0:
        print("[FAIL] No entities linked to articles.")
        sys.exit(1)

    # Check for specific entities (Example: 'Bangladesh')
    # Note: Regex might pick 'Bangladesh' as LOC
    bd_ent = session.query(Entity).filter(Entity.text.ilike('%Bangladesh%')).first()
    if bd_ent:
        print(f"Found known entity: {bd_ent.text} ({bd_ent.type})")
    else:
        print("[WARN] 'Bangladesh' not found as entity?")
        
    # Dump sample article entities
    article = session.query(Article).first()
    links = session.query(ArticleEntity).filter_by(article_id=article.id).all()
    print(f"Article {article.id} has {len(links)} entities:")
    for link in links:
        ent = session.query(Entity).get(link.entity_id)
        print(f" - {ent.text} ({ent.type})")

    print("[SUCCESS] Phase 5 verification passed.")

if __name__ == "__main__":
    verify_phase_5()
