"""
Migration script to add installs and trial_started columns to videos table
"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://anubhavmishra@localhost:5432/social_media_tracker")

# Try PostgreSQL, fallback to SQLite
try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    print("Connected to PostgreSQL database")
except Exception as e:
    print(f"PostgreSQL connection failed: {e}")
    print("Using SQLite for local development")
    DATABASE_URL = "sqlite:///./social_media_tracker.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    conn = engine.connect()

try:
    # Add installs column
    print("Adding installs column...")
    conn.execute(text("ALTER TABLE videos ADD COLUMN IF NOT EXISTS installs INTEGER DEFAULT 0"))
    print("✓ installs column added")

    # Add trial_started column
    print("Adding trial_started column...")
    conn.execute(text("ALTER TABLE videos ADD COLUMN IF NOT EXISTS trial_started INTEGER DEFAULT 0"))
    print("✓ trial_started column added")

    conn.commit()
    print("\n✓ Migration completed successfully!")

except Exception as e:
    print(f"Error during migration: {e}")
    conn.rollback()
finally:
    conn.close()
