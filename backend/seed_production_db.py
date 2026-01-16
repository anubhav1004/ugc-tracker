"""
Seed production database with accounts
Set DATABASE_URL environment variable to your Railway PostgreSQL URL
Example: export DATABASE_URL="postgresql://user:pass@host:port/dbname"
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Account, Base
from datetime import datetime

def seed_database(database_url):
    """Seed the database with initial accounts"""

    # Create engine with the provided DATABASE_URL
    engine = create_engine(database_url)

    # Create tables if they don't exist
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    accounts_data = [
        # Original accounts
        {"username": "professorcuriousaapp", "platform": "tiktok", "nickname": "Professor Curious"},
        {"username": "rose.studycorner", "platform": "tiktok", "nickname": "Rose Study Corner"},
        {"username": "piaprofessor", "platform": "tiktok", "nickname": "Pia Professor"},
        {"username": "succeedwjoseph", "platform": "tiktok", "nickname": "Succeed with Joseph"},
        {"username": "mari.curious", "platform": "tiktok", "nickname": "Mari Curious"},
        {"username": "max.curious1", "platform": "tiktok", "nickname": "Max Curious"},
        {"username": "karissa.curious", "platform": "tiktok", "nickname": "Karissa Curious"},
        # New accounts - Chloe
        {"username": "midn1ghtnova", "platform": "tiktok", "nickname": "Chloe"},
        {"username": "midn1ghtnova1", "platform": "instagram", "nickname": "Chloe"},
        # Sarah
        {"username": "waithearmeout46", "platform": "tiktok", "nickname": "Sarah"},
        {"username": "waithearmeout46", "platform": "instagram", "nickname": "Sarah"},
        # Arshia
        {"username": "swagdivafineshyt67", "platform": "tiktok", "nickname": "Arshia"},
        {"username": "swagdivafineshyt67", "platform": "instagram", "nickname": "Arshia"},
    ]

    try:
        added_count = 0
        skipped_count = 0

        for account_data in accounts_data:
            # Check if account already exists
            existing = db.query(Account).filter(
                Account.username == account_data['username'],
                Account.platform == account_data['platform']
            ).first()

            if existing:
                print(f"⚠️  Skipped {account_data['platform']}/@{account_data['username']} (already exists)")
                skipped_count += 1
                continue

            # Create profile URL
            profile_url = f"https://www.{account_data['platform']}.com/@{account_data['username']}"

            # Create new account
            account = Account(
                platform=account_data['platform'],
                username=account_data['username'],
                profile_url=profile_url,
                nickname=account_data['nickname'],
                is_active=True,
                created_at=datetime.utcnow()
            )

            db.add(account)
            print(f"✅ Added {account_data['platform']}/@{account_data['username']}")
            added_count += 1

        db.commit()

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"✅ Added: {added_count} accounts")
        print(f"⚠️  Skipped: {skipped_count} accounts (already exist)")
        print(f"{'='*60}")

        # Show all active accounts
        all_accounts = db.query(Account).filter(Account.is_active == True).all()
        print(f"\n📋 Total active accounts: {len(all_accounts)}")
        for acc in all_accounts:
            print(f"  - {acc.platform}/@{acc.username}")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # Check if DATABASE_URL is provided
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        print("\nUsage:")
        print('  export DATABASE_URL="postgresql://user:pass@host:port/dbname"')
        print("  python seed_production_db.py")
        print("\nOr:")
        print('  DATABASE_URL="postgresql://user:pass@host:port/dbname" python seed_production_db.py')
        sys.exit(1)

    print(f"Connecting to database...")
    print(f"URL: {database_url[:30]}...{database_url[-20:]}\n")

    success = seed_database(database_url)
    sys.exit(0 if success else 1)
