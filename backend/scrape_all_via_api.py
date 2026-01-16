"""
Scrape all videos from all accounts using the existing API endpoint
This doesn't require RapidAPI key if the scraper can work without it
"""

import requests
from database import SessionLocal, Account
import time

API_URL = "http://localhost:8000"


def main():
    """Scrape all account videos via API"""
    db = SessionLocal()

    try:
        # Get all active accounts
        accounts = db.query(Account).filter(Account.is_active == True).all()

        if not accounts:
            print("❌ No active accounts found")
            return

        print(f"\n🚀 Starting scrape for {len(accounts)} accounts")
        print("=" * 60)

        for i, account in enumerate(accounts, 1):
            print(f"\n[{i}/{len(accounts)}] Scraping @{account.username}...")

            profile_url = account.profile_url or f"https://www.tiktok.com/@{account.username}"

            try:
                # Call the scrape API endpoint
                response = requests.post(
                    f"{API_URL}/api/scrape/urls",
                    json={"urls": [profile_url]},
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    if result and len(result) > 0:
                        video_count = result[0].get('video_count', 0)
                        print(f"   ✅ Scraped {video_count} videos")
                    else:
                        print(f"   ⚠️  No data returned")
                else:
                    print(f"   ❌ Error: {response.status_code}")
                    if response.text:
                        print(f"   {response.text[:200]}")

            except requests.exceptions.Timeout:
                print(f"   ⏱️  Timeout - skipping")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

            # Delay between accounts
            if i < len(accounts):
                time.sleep(3)

        print("\n" + "=" * 60)
        print("✅ Scraping complete!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
