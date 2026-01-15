"""
Add is_spark_ad column to videos table
Migration script to add Spark Ads tracking support
"""

from sqlalchemy import text
from database import engine

def add_spark_ads_column():
    """Add is_spark_ad boolean column to videos table"""
    print("🔄 Adding is_spark_ad column to videos table...")

    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='videos' AND column_name='is_spark_ad';
        """))

        if result.fetchone():
            print("✅ is_spark_ad column already exists!")
            return

        # Add the column
        conn.execute(text("""
            ALTER TABLE videos
            ADD COLUMN is_spark_ad BOOLEAN DEFAULT FALSE;
        """))
        conn.commit()
        print("✅ is_spark_ad column added successfully!")

        # Update existing videos to be marked as organic (not ads)
        conn.execute(text("""
            UPDATE videos
            SET is_spark_ad = FALSE
            WHERE is_spark_ad IS NULL;
        """))
        conn.commit()
        print("✅ All existing videos marked as organic (not Spark Ads)")

if __name__ == "__main__":
    try:
        add_spark_ads_column()
        print("\n🎉 Migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
