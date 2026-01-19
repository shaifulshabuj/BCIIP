import os
import sys
from sqlalchemy import create_engine
from services.api.models import Base, Entity, ArticleEntity

def create_tables():
    print("Creating entity tables...")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    engine = create_engine(DATABASE_URL)
    
    try:
        # Create tables if they don't exist
        # This will verify models matches DB schema for new tables
        Base.metadata.create_all(engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
