"""
Bulk add TikTok accounts using RapidAPI
This WORKS because RapidAPI handles all anti-bot protection
"""

import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal, Video, Account, Collection, VideoCollection
from scrapers.rapidapi_tiktok_scraper import RapidAPITikTokScraper
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Profile URLs to add
PROFILE_URLS = [
    "https://www.tiktok.com/@rose.studycorner",
    "https://www.tiktok.com/@piaprofessor",
    "https://www.tiktok.com/@succeedwjoseph",
    "https://www.tiktok.com/@mari.curious",
    "https://www.tiktok.com/@max.curious1",
    "https://www.tiktok.com/@karissa.curious",
    "https://www.tiktok.com/@professorcuriousaapp"
]


def create_or_update_account(db: Session, video: Video):
    """Create or update account from video data"""
    if not video.author_username:
        return None

    account = db.query(Account).filter(
        Account.username == video.author_username,
        Account.platform == video.platform
    ).first()

    if account:
        account.last_scraped = datetime.utcnow()
        account.avatar = video.author_avatar or account.avatar
        account.nickname = video.author_nickname or account.nickname
    else:
        account = Account(
            username=video.author_username,
            platform=video.platform,
            nickname=video.author_nickname,
            avatar=video.author_avatar,
            profile_url=f"https://www.tiktok.com/@{video.author_username}",
            total_videos=0,
            total_views=0,
            total_likes=0,
            total_followers=0
        )
        db.add(account)

    db.commit()
    db.refresh(account)

    # Refresh stats
    videos = db.query(Video).filter(
        Video.author_username == account.username,
        Video.platform == account.platform
    ).all()

    account.total_videos = len(videos)
    account.total_views = sum(v.views for v in videos)
    account.total_likes = sum(v.likes for v in videos)
    db.commit()

    return account


def add_accounts_rapidapi():
    """Add all accounts using RapidAPI"""

    print("🚀 Starting bulk account import with RapidAPI...")
    print(f"📋 Adding {len(PROFILE_URLS)} accounts")
    print("✅ Using RapidAPI - No anti-bot issues!\n")

    # Check for API key
    api_key = os.getenv('RAPIDAPI_KEY')
    if not api_key:
        print("❌ RapidAPI key not found!")
        print("\n📝 Setup instructions:")
        print("1. Go to: https://rapidapi.com/tikwm-tikwm-default/api/tiktok-scraper7")
        print("2. Sign up / Log in")
        print("3. Subscribe to the FREE plan (120 requests/min)")
        print("4. Copy your API key")
        print("5. Add to backend/.env:")
        print("   RAPIDAPI_KEY=your_key_here")
        print("\nThen run this script again.")
        return

    db = SessionLocal()

    # Get or create default collection
    default_collection = db.query(Collection).filter(Collection.is_default == True).first()
    if not default_collection:
        default_collection = Collection(
            name="Default",
            is_default=True,
            description="All tracked videos"
        )
        db.add(default_collection)
        db.commit()
        db.refresh(default_collection)

    total_videos = 0
    total_accounts = 0
    errors = []

    # Initialize scraper
    try:
        scraper = RapidAPITikTokScraper(api_key=api_key)
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
        return

    for idx, url in enumerate(PROFILE_URLS, 1):
        username = url.split('@')[1].split('?')[0].split('/')[0]
        print(f"\n{'='*60}")
        print(f"[{idx}/{len(PROFILE_URLS)}] Processing @{username}")
        print(f"{'='*60}")

        try:
            # Scrape profile - get last 10 videos
            profile_data = scraper.scrape_profile(url, limit=10)

            if not profile_data['videos']:
                print(f"⚠️  No videos found for @{username}")
                errors.append({"url": url, "error": "No videos found"})
                continue

            videos_added = 0
            videos_updated = 0

            for video_data in profile_data['videos']:
                if not video_data or not video_data.get('id'):
                    continue

                # Check if video exists
                existing = db.query(Video).filter(
                    Video.id == video_data['id'],
                    Video.platform == 'tiktok'
                ).first()

                if existing:
                    # Update existing video
                    for key, value in video_data.items():
                        if key not in ['id', 'platform', 'created_at']:
                            setattr(existing, key, value)
                    existing.scraped_at = datetime.utcnow()
                    db.commit()
                    video = existing
                    videos_updated += 1
                else:
                    # Create new video
                    video = Video(**video_data)
                    db.add(video)
                    db.commit()
                    db.refresh(video)
                    videos_added += 1

                # Add to collection
                existing_vc = db.query(VideoCollection).filter(
                    VideoCollection.video_id == video.id,
                    VideoCollection.collection_id == default_collection.id
                ).first()

                if not existing_vc:
                    vc = VideoCollection(
                        video_id=video.id,
                        collection_id=default_collection.id
                    )
                    db.add(vc)
                    db.commit()

            # Create/update account
            if profile_data['videos']:
                sample_video = db.query(Video).filter(
                    Video.id == profile_data['videos'][0]['id']
                ).first()

                if sample_video:
                    account = create_or_update_account(db, sample_video)
                    total_accounts += 1
                    total_videos += videos_added

                    print(f"\n✅ Success:")
                    print(f"   • Account: @{username}")
                    print(f"   • New videos: {videos_added}")
                    print(f"   • Updated videos: {videos_updated}")
                    print(f"   • Total videos: {len(profile_data['videos'])}")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            errors.append({"url": url, "error": str(e)})
            import traceback
            traceback.print_exc()

    db.close()

    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 Bulk import complete!")
    print(f"{'='*60}")
    print(f"✅ Accounts processed: {total_accounts}/{len(PROFILE_URLS)}")
    print(f"✅ New videos added: {total_videos}")

    if errors:
        print(f"\n⚠️  Errors encountered: {len(errors)}")
        for error in errors:
            username = error['url'].split('@')[1].split('?')[0].split('/')[0]
            print(f"   • @{username}: {error['error']}")

    print(f"\n{'='*60}")
    print(f"📊 View your dashboard at http://localhost:3000")
    print(f"🔄 Daily updates run automatically at midnight")
    print(f"{'='*60}")


if __name__ == "__main__":
    add_accounts_rapidapi()
