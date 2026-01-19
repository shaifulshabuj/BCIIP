import os
import sys
from sqlalchemy import create_engine, text

def add_columns():
    print("Adding summary columns to articles table...")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/bciip")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE articles ADD COLUMN IF NOT EXISTS summary_text TEXT;"))
            conn.execute(text("ALTER TABLE articles ADD COLUMN IF NOT EXISTS summary_bullets TEXT;"))
            conn.commit()
        print("Columns added successfully.")
    except Exception as e:
        print(f"Error adding columns: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_columns()
