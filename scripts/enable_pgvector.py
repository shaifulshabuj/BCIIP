import os
import sys
from sqlalchemy import create_engine, text

def enable_pgvector():
    print("Enabling pgvector extension and adding embedding column...")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    # For enabling extension, we might need superuser, relying on user permissions
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Enable extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            
            # Add column if not exists (raw SQL)
            # Note: models.py has Vector(384)
            conn.execute(text("ALTER TABLE articles ADD COLUMN IF NOT EXISTS embedding vector(384);"))
            
            conn.commit()
        print("pgvector enabled and column added.")
    except Exception as e:
        print(f"Error enabling pgvector: {e}")
        sys.exit(1)

if __name__ == "__main__":
    enable_pgvector()
