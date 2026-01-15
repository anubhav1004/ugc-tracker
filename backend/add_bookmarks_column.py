"""
Add bookmarks column to videos table
"""

from sqlalchemy import text
from database import engine

def add_bookmarks_column():
    """Add bookmarks column to videos table"""

    print("📋 Adding bookmarks column to videos table...")

    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='videos' AND column_name='bookmarks';
            """))

            if result.fetchone():
                print("✅ Bookmarks column already exists!")
                return True

            # Add the column
            conn.execute(text("""
                ALTER TABLE videos
                ADD COLUMN bookmarks INTEGER DEFAULT 0;
            """))
            conn.commit()

            print("✅ Bookmarks column added successfully!")
            return True

    except Exception as e:
        print(f"❌ Error adding bookmarks column: {e}")
        return False

if __name__ == "__main__":
    add_bookmarks_column()
