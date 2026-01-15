"""
Setup Supabase Database
Creates all tables and initial data
"""

import sys
from database import init_db, SessionLocal, Collection

def setup_supabase():
    """Initialize Supabase database with all tables"""

    print("🚀 Setting up Supabase database...")

    try:
        # Create all tables
        print("📋 Creating database tables...")
        init_db()
        print("✅ All tables created successfully!")

        # Create default collection
        print("📁 Creating default collection...")
        db = SessionLocal()

        existing = db.query(Collection).filter(Collection.is_default == True).first()
        if not existing:
            default_collection = Collection(
                name="Default",
                description="All tracked videos",
                is_default=True,
                color="#8B5CF6",
                icon="folder"
            )
            db.add(default_collection)
            db.commit()
            print("✅ Default collection created!")
        else:
            print("✅ Default collection already exists!")

        db.close()

        print("\n" + "="*50)
        print("🎉 Supabase setup complete!")
        print("="*50)
        print("\nYour database is ready with:")
        print("  ✅ 9 tables created")
        print("  ✅ All indexes added")
        print("  ✅ Default collection created")
        print("\nYou can now start the backend:")
        print("  python main.py")
        print("="*50)

        return True

    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        print("\nPlease check:")
        print("  1. Your DATABASE_URL in .env is correct")
        print("  2. Your Supabase project is running")
        print("  3. Your database password is correct")
        return False

if __name__ == "__main__":
    success = setup_supabase()
    sys.exit(0 if success else 1)
