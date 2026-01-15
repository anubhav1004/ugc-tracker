"""
Lightweight Bulk Account Import
Only scrapes last 2 videos per profile to avoid anti-bot detection
Daily updater will fill in detailed stats later
"""

import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal, Video, Account, Collection, VideoCollection
from scrapers.lightweight_profile_scraper import LightweightProfileScraper
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


def create_or_update_account(db: Session, username: str, followers: int, profile_url: str):
    """Create or update account"""
    account = db.query(Account).filter(
        Account.username == username,
        Account.platform == 'tiktok'
    ).first()

    if account:
        account.last_scraped = datetime.utcnow()
        account.total_followers = followers
    else:
        account = Account(
            username=username,
            platform='tiktok',
            nickname=username,
            avatar=None,
            profile_url=profile_url,
            total_videos=0,
            total_views=0,
            total_likes=0,
            total_followers=followers
        )
        db.add(account)

    db.commit()
    db.refresh(account)

    # Refresh stats from videos
    videos = db.query(Video).filter(
        Video.author_username == account.username,
        Video.platform == 'tiktok'
    ).all()

    account.total_videos = len(videos)
    account.total_views = sum(v.views for v in videos)
    account.total_likes = sum(v.likes for v in videos)
    db.commit()

    return account


async def add_accounts_lightweight():
    """Add accounts with lightweight scraping (only last 2 videos)"""

    print("🚀 Starting lightweight account import...")
    print(f"📋 Adding {len(PROFILE_URLS)} accounts (last 2 videos each)")
    print("⚡ This is much faster and avoids anti-bot detection")
    print("📅 Run daily_stats_updater.py daily to keep stats fresh\n")

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

    async with LightweightProfileScraper() as scraper:
        for idx, url in enumerate(PROFILE_URLS, 1):
            username = url.split('@')[1].split('?')[0].split('/')[0]

            print(f"\n{'='*60}")
            print(f"[{idx}/{len(PROFILE_URLS)}] Processing @{username}")
            print(f"{'='*60}")

            try:
                # Lightweight scrape - only last 2 videos
                profile_data = await scraper.scrape_profile_light(url)

                if not profile_data['videos']:
                    print(f"⚠️  No videos found for @{username}")
                    errors.append({"url": url, "error": "No videos found"})

                    # Still create account record with follower count
                    if profile_data.get('followers', 0) > 0:
                        create_or_update_account(db, username, profile_data['followers'], url)
                        total_accounts += 1

                    continue

                videos_added = 0
                videos_updated = 0

                # Add videos to database
                for video_data in profile_data['videos']:
                    if not video_data or not video_data.get('id'):
                        continue

                    # Check if video exists
                    existing = db.query(Video).filter(
                        Video.id == video_data['id'],
                        Video.platform == 'tiktok'
                    ).first()

                    if existing:
                        # Update existing
                        for key, value in video_data.items():
                            if key not in ['id', 'platform', 'created_at']:
                                setattr(existing, key, value)
                        existing.scraped_at = datetime.utcnow()
                        db.commit()
                        video = existing
                        videos_updated += 1
                    else:
                        # Create new
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
                account = create_or_update_account(
                    db,
                    username,
                    profile_data.get('followers', 0),
                    url
                )

                total_accounts += 1
                total_videos += videos_added

                print(f"\n✅ Success:")
                print(f"   • Account: @{username}")
                print(f"   • Followers: {profile_data.get('followers', 0):,}")
                print(f"   • New videos: {videos_added}")
                print(f"   • Updated videos: {videos_updated}")
                print(f"   • Total videos tracked: {len(profile_data['videos'])}")

                # Rate limiting - wait between profiles
                if idx < len(PROFILE_URLS):
                    print(f"\n⏳ Waiting 3 seconds before next profile...")
                    await asyncio.sleep(3)

            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                errors.append({"url": url, "error": str(e)})
                import traceback
                traceback.print_exc()

    db.close()

    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 Lightweight import complete!")
    print(f"{'='*60}")
    print(f"✅ Accounts added: {total_accounts}/{len(PROFILE_URLS)}")
    print(f"✅ Videos added: {total_videos}")

    if errors:
        print(f"\n⚠️  Issues encountered: {len(errors)}")
        for error in errors:
            username = error['url'].split('@')[1].split('?')[0].split('/')[0]
            print(f"   • @{username}: {error['error']}")

    print(f"\n{'='*60}")
    print(f"📅 NEXT STEPS:")
    print(f"{'='*60}")
    print(f"1. Run 'python daily_stats_updater.py' to fetch full video stats")
    print(f"2. Set up a daily cron job to keep stats updated")
    print(f"3. View your dashboard at http://localhost:3000")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(add_accounts_lightweight())
