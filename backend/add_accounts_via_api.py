"""
Add accounts to production database via API
"""
import requests
import time

API_URL = "https://ugc-tracker-backend-prod.up.railway.app"

accounts = [
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

def add_account(account):
    """Add a single account via API"""
    try:
        profile_url = f"https://www.{account['platform']}.com/@{account['username']}"

        response = requests.post(
            f"{API_URL}/api/accounts",
            json={
                "username": account["username"],
                "platform": account["platform"],
                "profile_url": profile_url,
                "nickname": account["nickname"],
                "is_active": True
            },
            timeout=10
        )

        if response.status_code in [200, 201]:
            print(f"✅ Added {account['platform']}/@{account['username']}")
            return True
        elif response.status_code == 409:
            print(f"⚠️  Skipped {account['platform']}/@{account['username']} (already exists)")
            return True
        else:
            print(f"❌ Failed to add {account['platform']}/@{account['username']}: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error adding {account['platform']}/@{account['username']}: {str(e)}")
        return False

def main():
    print(f"Adding accounts to {API_URL}")
    print("=" * 60)

    added = 0
    failed = 0

    for account in accounts:
        if add_account(account):
            added += 1
        else:
            failed += 1
        time.sleep(0.5)  # Small delay between requests

    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"✅ Added/Existing: {added}")
    print(f"❌ Failed: {failed}")
    print("=" * 60)

if __name__ == "__main__":
    main()
