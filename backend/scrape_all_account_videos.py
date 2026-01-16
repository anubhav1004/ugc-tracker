"""
Scrape ALL videos from all tracked accounts using RapidAPI
This will fetch the complete video history for each account
"""

import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal, Video, Account
from scrapers.rapidapi_tiktok_scraper import RapidAPITikTokScraper
from datetime import datetime
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()


def scrape_account_videos(db: Session, account: Account, max_videos: int = 100):
    """Scrape all videos for a given account"""
    print(f"\n{'='*60}")
    print(f"Scraping videos for @{account.username}")
    print(f"{'='*60}")

    scraper = RapidAPITikTokScraper()

    try:
        # Fetch videos from the account
        videos_data = scraper.get_user_posts(account.username, count=max_videos)

        if not videos_data:
            print(f"❌ No videos found for @{account.username}")
            return 0

        print(f"📥 Found {len(videos_data)} videos")

        saved_count = 0
        updated_count = 0

        for video_data in videos_data:
            # Check if video already exists
            existing = db.query(Video).filter(
                Video.id == video_data['id'],
                Video.platform == video_data['platform']
            ).first()

            if existing:
                # Update existing video stats
                existing.views = video_data.get('views', existing.views)
                existing.likes = video_data.get('likes', existing.likes)
                existing.comments = video_data.get('comments', existing.comments)
                existing.shares = video_data.get('shares', existing.shares)
                existing.bookmarks = video_data.get('bookmarks', existing.bookmarks)
                existing.scraped_at = datetime.utcnow()

                # Add install and trial data (simulate based on views for now)
                if not existing.installs or existing.installs == 0:
                    install_rate = random.uniform(0.01, 0.05)
                    existing.installs = int(existing.views * install_rate) if existing.views else 0
                    trial_rate = random.uniform(0.2, 0.4)
                    existing.trial_started = int(existing.installs * trial_rate)

                updated_count += 1
            else:
                # Create new video
                video = Video(
                    id=video_data['id'],
                    platform=video_data['platform'],
                    url=video_data['url'],
                    thumbnail=video_data.get('thumbnail'),
                    caption=video_data.get('caption'),
                    author_username=video_data.get('author_username'),
                    author_nickname=video_data.get('author_nickname'),
                    author_avatar=video_data.get('author_avatar'),
                    author_id=video_data.get('author_id'),
                    views=video_data.get('views', 0),
                    likes=video_data.get('likes', 0),
                    comments=video_data.get('comments', 0),
                    shares=video_data.get('shares', 0),
                    bookmarks=video_data.get('bookmarks', 0),
                    music_id=video_data.get('music_id'),
                    music_title=video_data.get('music_title'),
                    music_author=video_data.get('music_author'),
                    music_url=video_data.get('music_url'),
                    hashtags=video_data.get('hashtags', []),
                    mentions=video_data.get('mentions', []),
                    duration=video_data.get('duration'),
                    posted_at=video_data.get('posted_at'),
                    scraped_at=datetime.utcnow()
                )

                # Add install and trial data (simulate based on views)
                if video.views:
                    install_rate = random.uniform(0.01, 0.05)
                    video.installs = int(video.views * install_rate)
                    trial_rate = random.uniform(0.2, 0.4)
                    video.trial_started = int(video.installs * trial_rate)
                else:
                    video.installs = 0
                    video.trial_started = 0

                db.add(video)
                saved_count += 1

        # Update account stats
        account.last_scraped = datetime.utcnow()
        account.total_videos = len(videos_data)

        db.commit()

        print(f"✅ Saved {saved_count} new videos, updated {updated_count} existing videos")
        return saved_count

    except Exception as e:
        print(f"❌ Error scraping @{account.username}: {str(e)}")
        db.rollback()
        return 0


def main():
    """Main function to scrape all accounts"""
    db = SessionLocal()

    try:
        # Get all active accounts
        accounts = db.query(Account).filter(Account.is_active == True).all()

        if not accounts:
            print("❌ No active accounts found in database")
            return

        print(f"\n🚀 Starting scrape for {len(accounts)} accounts")
        print("=" * 60)

        total_new_videos = 0

        for account in accounts:
            new_videos = scrape_account_videos(db, account, max_videos=100)
            total_new_videos += new_videos

            # Small delay between accounts to avoid rate limiting
            import time
            time.sleep(2)

        print("\n" + "=" * 60)
        print(f"✅ Scraping complete!")
        print(f"📊 Total new videos added: {total_new_videos}")
        print(f"👥 Accounts processed: {len(accounts)}")

        # Show final stats
        total_videos = db.query(Video).count()
        print(f"📹 Total videos in database: {total_videos}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
