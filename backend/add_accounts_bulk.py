"""
Bulk add TikTok accounts
"""

import asyncio
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, Video, Account, Collection, VideoCollection
from scrapers.url_scraper import URLScraper
from datetime import datetime

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

async def add_accounts():
    """Add all accounts"""

    print("🚀 Starting bulk account import...")
    print(f"📋 Adding {len(PROFILE_URLS)} accounts\n")

    db = SessionLocal()

    # Get or create default collection
    default_collection = db.query(Collection).filter(Collection.is_default == True).first()
    if not default_collection:
        default_collection = Collection(name="Default", is_default=True)
        db.add(default_collection)
        db.commit()
        db.refresh(default_collection)

    total_videos = 0
    total_accounts = 0
    errors = []

    async with URLScraper() as scraper:
        for idx, url in enumerate(PROFILE_URLS, 1):
            username = url.split('@')[1].split('?')[0]
            print(f"\n[{idx}/{len(PROFILE_URLS)}] Processing @{username}...")

            try:
                # Detect URL type
                url_type = scraper.detect_url_type(url)

                if url_type == 'profile':
                    print(f"  📹 Scraping profile videos...")
                    profile_data = await scraper.scrape_profile(url, limit=50)

                    videos_added = 0
                    for video_data in profile_data['videos']:
                        # Check if video exists
                        existing = db.query(Video).filter(
                            Video.id == video_data['id'],
                            Video.platform == video_data['platform']
                        ).first()

                        if existing:
                            # Update
                            for key, value in video_data.items():
                                setattr(existing, key, value)
                            db.commit()
                            video = existing
                        else:
                            # Create new
                            video = Video(**video_data)
                            db.add(video)
                            db.commit()
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
                            print(f"  ✅ Added @{username}: {videos_added} new videos, {len(profile_data['videos'])} total")
                            total_videos += videos_added

                else:
                    print(f"  ⚠️  Not a profile URL, skipping")

            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                errors.append({"url": url, "error": str(e)})

    db.close()

    # Summary
    print("\n" + "="*60)
    print("🎉 Bulk import complete!")
    print("="*60)
    print(f"✅ Accounts added: {total_accounts}")
    print(f"✅ Videos added: {total_videos}")
    if errors:
        print(f"⚠️  Errors: {len(errors)}")
        for error in errors:
            print(f"   - {error['url']}: {error['error']}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(add_accounts())
