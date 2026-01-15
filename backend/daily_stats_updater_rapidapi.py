"""
Daily Stats Updater using RapidAPI
Updates all video statistics daily using RapidAPI (no anti-bot issues)
"""

from sqlalchemy.orm import Session
from database import SessionLocal, Video, Account
from scrapers.rapidapi_tiktok_scraper import RapidAPITikTokScraper
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def update_all_stats():
    """Update stats for all videos using RapidAPI"""

    print("🔄 Starting daily stats update with RapidAPI...")
    print(f"⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    # Check for API key
    api_key = os.getenv('RAPIDAPI_KEY')
    if not api_key:
        print("❌ RapidAPI key not found in .env file!")
        return

    db = SessionLocal()

    try:
        # Get all TikTok videos
        videos = db.query(Video).filter(Video.platform == 'tiktok').all()

        print(f"📊 Found {len(videos)} videos to update\n")

        if not videos:
            print("⚠️  No videos found in database. Run add_accounts_rapidapi.py first.")
            return

        # Initialize scraper
        scraper = RapidAPITikTokScraper(api_key=api_key)

        updated_count = 0
        error_count = 0

        for idx, video in enumerate(videos, 1):
            print(f"[{idx}/{len(videos)}] Updating video {video.id}...")
            print(f"  @{video.author_username}")

            try:
                # Fetch updated video info
                video_data = scraper.get_video_info(video.url)

                if video_data:
                    # Update video in database
                    video.views = video_data.get('views', video.views)
                    video.likes = video_data.get('likes', video.likes)
                    video.comments = video_data.get('comments', video.comments)
                    video.shares = video_data.get('shares', video.shares)
                    video.bookmarks = video_data.get('bookmarks', video.bookmarks)
                    video.caption = video_data.get('caption', video.caption)
                    video.thumbnail = video_data.get('thumbnail', video.thumbnail)
                    video.scraped_at = datetime.utcnow()

                    db.commit()
                    updated_count += 1

                    print(f"  ✓ Updated - Views: {video.views:,}, Likes: {video.likes:,}")
                else:
                    print(f"  ⚠️  Could not fetch stats")
                    error_count += 1

            except Exception as e:
                print(f"  ✗ Error: {e}")
                error_count += 1

        # Update account stats
        print(f"\n📈 Updating account statistics...")
        accounts = db.query(Account).filter(Account.platform == 'tiktok').all()

        for account in accounts:
            account_videos = db.query(Video).filter(
                Video.author_username == account.username,
                Video.platform == 'tiktok'
            ).all()

            account.total_videos = len(account_videos)
            account.total_views = sum(v.views for v in account_videos)
            account.total_likes = sum(v.likes for v in account_videos)
            account.last_scraped = datetime.utcnow()

        db.commit()

        # Summary
        print(f"\n{'='*60}")
        print(f"✅ Daily update complete!")
        print(f"{'='*60}")
        print(f"Videos updated: {updated_count}/{len(videos)}")
        print(f"Errors: {error_count}")
        print(f"Accounts updated: {len(accounts)}")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ Error during update: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    update_all_stats()
