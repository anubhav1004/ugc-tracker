"""
Scrape all videos from karissa.curious profile
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Set RapidAPI key from .env file
os.environ['RAPIDAPI_KEY'] = 'a4181840f6msh08a6c48170b4509p1be25cjsn5b0ce987b6e8'

from scrapers.rapidapi_tiktok_scraper import RapidAPITikTokScraper
from database import SessionLocal, Video
from sqlalchemy import text
from datetime import datetime
import time

def scrape_karissa():
    """Scrape karissa.curious profile and add videos to database"""

    # Initialize scraper
    scraper = RapidAPITikTokScraper()

    # Karissa's profile
    profile_url = "https://www.tiktok.com/@karissa.curious"
    username = "karissa.curious"

    print(f"\n{'='*70}")
    print(f"Scraping @{username}")
    print(f"{'='*70}\n")

    # Try to get maximum videos (35 is the API limit)
    print("Fetching videos from RapidAPI (max 35 per call)...")
    videos = scraper.get_user_posts(username, count=35)

    if not videos:
        print("❌ No videos fetched from API")
        return

    print(f"✓ Fetched {len(videos)} videos from API\n")

    # Connect to database
    db = SessionLocal()

    try:
        new_count = 0
        updated_count = 0

        for i, video_data in enumerate(videos, 1):
            video_id = video_data['id']

            # Check if video already exists
            existing = db.query(Video).filter(Video.id == video_id).first()

            if existing:
                # Update existing video stats
                existing.views = video_data['views']
                existing.likes = video_data['likes']
                existing.comments = video_data['comments']
                existing.shares = video_data['shares']
                existing.bookmarks = video_data.get('bookmarks', 0)
                existing.scraped_at = datetime.utcnow()
                updated_count += 1
                print(f"[{i}/{len(videos)}] Updated: {video_id} - {video_data['views']:,} views")
            else:
                # Create new video
                video = Video(**video_data)
                db.add(video)
                new_count += 1
                posted = video_data.get('posted_at', 'Unknown')
                print(f"[{i}/{len(videos)}] New: {video_id} - Posted: {posted} - {video_data['views']:,} views")

        # Commit all changes
        db.commit()

        print(f"\n{'='*70}")
        print(f"✅ Scraping complete!")
        print(f"   New videos: {new_count}")
        print(f"   Updated videos: {updated_count}")
        print(f"   Total processed: {len(videos)}")
        print(f"{'='*70}\n")

        # Show total videos in database for karissa
        total = db.query(Video).filter(Video.author_username == username).count()
        print(f"📊 Total videos in database for @{username}: {total}")

        # Note about API limitation
        if len(videos) == 35:
            print(f"\n⚠️  Note: RapidAPI returned the maximum 35 videos.")
            print(f"   If @{username} has more videos, we would need:")
            print(f"   1. A different API with pagination support")
            print(f"   2. Or manually add video URLs")
            print(f"   3. Or use TikTok's official API")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    scrape_karissa()
