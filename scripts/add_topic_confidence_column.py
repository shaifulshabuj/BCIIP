import os
import sys
from sqlalchemy import create_engine, text

def add_column():
    print("Adding topic_confidence column to articles table...")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE articles ADD COLUMN IF NOT EXISTS topic_confidence VARCHAR;"))
            conn.commit()
        print("Column added successfully.")
    except Exception as e:
        print(f"Error adding column: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_column()
