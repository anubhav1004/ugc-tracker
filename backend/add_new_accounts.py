"""
Add new accounts to the database
"""
from sqlalchemy.orm import Session
from database import SessionLocal, Account
from datetime import datetime

def add_accounts():
    """Add new accounts to track"""
    db = SessionLocal()

    accounts_data = [
        # Chloe
        {
            'platform': 'tiktok',
            'username': 'midn1ghtnova',
            'profile_url': 'https://www.tiktok.com/@midn1ghtnova',
            'nickname': 'Chloe',
            'is_active': True
        },
        {
            'platform': 'instagram',
            'username': 'midn1ghtnova1',
            'profile_url': 'https://www.instagram.com/midn1ghtnova1',
            'nickname': 'Chloe',
            'is_active': True
        },
        # Sarah
        {
            'platform': 'tiktok',
            'username': 'waithearmeout46',
            'profile_url': 'https://www.tiktok.com/@waithearmeout46',
            'nickname': 'Sarah',
            'is_active': True
        },
        {
            'platform': 'instagram',
            'username': 'waithearmeout46',
            'profile_url': 'https://www.instagram.com/waithearmeout46',
            'nickname': 'Sarah',
            'is_active': True
        },
        # Arshia
        {
            'platform': 'tiktok',
            'username': 'swagdivafineshyt67',
            'profile_url': 'https://www.tiktok.com/@swagdivafineshyt67',
            'nickname': 'Arshia',
            'is_active': True
        },
        {
            'platform': 'instagram',
            'username': 'swagdivafineshyt67',
            'profile_url': 'https://www.instagram.com/swagdivafineshyt67',
            'nickname': 'Arshia',
            'is_active': True
        }
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

            # Create new account
            account = Account(
                platform=account_data['platform'],
                username=account_data['username'],
                profile_url=account_data['profile_url'],
                nickname=account_data['nickname'],
                is_active=account_data['is_active'],
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

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_accounts()
