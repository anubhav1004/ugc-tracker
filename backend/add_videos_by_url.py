"""
Add videos by direct URL
This works because we're accessing individual video pages, not scraping profiles
"""

import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal, Video, Account, Collection, VideoCollection
from scrapers.playwright_tiktok_scraper import PlaywrightTikTokScraper
from datetime import datetime

# Direct video URLs for each account (2-3 recent videos each)
VIDEO_URLS = [
    # @rose.studycorner - Add 2-3 video URLs here
    "https://www.tiktok.com/@rose.studycorner/video/XXXXXXXXX",
    "https://www.tiktok.com/@rose.studycorner/video/XXXXXXXXX",

    # @piaprofessor - Add 2-3 video URLs here
    "https://www.tiktok.com/@piaprofessor/video/XXXXXXXXX",
    "https://www.tiktok.com/@piaprofessor/video/XXXXXXXXX",

    # @succeedwjoseph - Add 2-3 video URLs here
    "https://www.tiktok.com/@succeedwjoseph/video/XXXXXXXXX",
    "https://www.tiktok.com/@succeedwjoseph/video/XXXXXXXXX",

    # @mari.curious - Add 2-3 video URLs here
    "https://www.tiktok.com/@mari.curious/video/XXXXXXXXX",
    "https://www.tiktok.com/@mari.curious/video/XXXXXXXXX",

    # @max.curious1 - Add 2-3 video URLs here
    "https://www.tiktok.com/@max.curious1/video/XXXXXXXXX",
    "https://www.tiktok.com/@max.curious1/video/XXXXXXXXX",

    # @karissa.curious - Add 2-3 video URLs here
    "https://www.tiktok.com/@karissa.curious/video/XXXXXXXXX",
    "https://www.tiktok.com/@karissa.curious/video/XXXXXXXXX",

    # @professorcuriousaapp - Add 2-3 video URLs here
    "https://www.tiktok.com/@professorcuriousaapp/video/XXXXXXXXX",
    "https://www.tiktok.com/@professorcuriousaapp/video/XXXXXXXXX",
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


async def add_videos():
    """Add videos by URL"""

    print("🚀 Adding videos by direct URL...")
    print("💡 This works because we're accessing individual videos, not scraping profiles")
    print(f"📹 Processing {len(VIDEO_URLS)} video URLs\n")

    # Filter out placeholder URLs
    valid_urls = [url for url in VIDEO_URLS if 'XXXXXXXXX' not in url]

    if not valid_urls:
        print("❌ No valid video URLs found!")
        print("📝 Please edit add_videos_by_url.py and replace XXXXXXXXX with real video IDs")
        print("\nHow to get video URLs:")
        print("1. Visit each TikTok profile in your browser")
        print("2. Right-click on the first 2-3 videos")
        print("3. Select 'Copy link'")
        print("4. Paste into the VIDEO_URLS list in this file")
        return

    print(f"✅ Found {len(valid_urls)} valid video URLs\n")

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

    videos_added = 0
    videos_updated = 0
    errors = []

    async with PlaywrightTikTokScraper() as scraper:
        for idx, url in enumerate(valid_urls, 1):
            print(f"[{idx}/{len(valid_urls)}] Scraping video...")
            print(f"  URL: {url}")

            try:
                # Scrape individual video
                video_data = await scraper.scrape_video(url)

                if not video_data:
                    print(f"  ✗ Failed to scrape")
                    errors.append(url)
                    continue

                # Check if exists
                existing = db.query(Video).filter(
                    Video.id == video_data['id'],
                    Video.platform == video_data['platform']
                ).first()

                if existing:
                    # Update
                    for key, value in video_data.items():
                        if key not in ['id', 'platform', 'created_at']:
                            setattr(existing, key, value)
                    existing.scraped_at = datetime.utcnow()
                    db.commit()
                    video = existing
                    videos_updated += 1
                    print(f"  ✓ Updated - @{video_data['author_username']}")
                else:
                    # Create
                    video = Video(**video_data)
                    db.add(video)
                    db.commit()
                    db.refresh(video)
                    videos_added += 1
                    print(f"  ✓ Added - @{video_data['author_username']}")

                print(f"    Views: {video_data.get('views', 0):,}, Likes: {video_data.get('likes', 0):,}")

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
                create_or_update_account(db, video)

                # Rate limiting
                if idx < len(valid_urls):
                    print(f"  ⏳ Waiting 3 seconds...")
                    await asyncio.sleep(3)

            except Exception as e:
                print(f"  ✗ Error: {e}")
                errors.append(url)

    db.close()

    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 Video import complete!")
    print(f"{'='*60}")
    print(f"✅ Videos added: {videos_added}")
    print(f"✅ Videos updated: {videos_updated}")
    print(f"❌ Errors: {len(errors)}")
    print(f"{'='*60}")

    if videos_added > 0:
        print(f"\n📊 View your dashboard at http://localhost:3000")
        print(f"🔄 Run 'python daily_stats_updater.py' daily to keep stats fresh")


if __name__ == "__main__":
    asyncio.run(add_videos())
