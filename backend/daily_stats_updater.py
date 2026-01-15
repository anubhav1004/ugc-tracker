"""
Daily Stats Updater
Runs daily to update statistics for all tracked videos
This keeps data fresh without triggering anti-bot detection
"""

import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal, Video, Account
from datetime import datetime
from playwright.async_api import async_playwright
import json
import re
from typing import Optional, Dict


class DailyStatsUpdater:
    """Updates video statistics daily"""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def update_video_stats(self, video_url: str) -> Optional[Dict]:
        """
        Fetch updated stats for a single video
        """
        try:
            page = await self.context.new_page()

            # Navigate to video
            await page.goto(video_url, wait_until='domcontentloaded', timeout=30000)

            # Wait for content
            await page.wait_for_timeout(2000)

            # Extract page content
            content = await page.content()

            await page.close()

            # Extract JSON data
            json_match = re.search(
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                content
            )

            if not json_match:
                return None

            page_data = json.loads(json_match.group(1))

            # Extract video stats
            stats = self._extract_video_stats(page_data)

            return stats

        except Exception as e:
            print(f"  Error updating video stats: {e}")
            return None

    def _extract_video_stats(self, data: Dict) -> Optional[Dict]:
        """Extract video statistics from page JSON"""
        try:
            if '__DEFAULT_SCOPE__' not in data:
                return None

            default_scope = data['__DEFAULT_SCOPE__']

            if 'webapp.video-detail' not in default_scope:
                return None

            video_detail = default_scope['webapp.video-detail']

            if 'itemInfo' not in video_detail or 'itemStruct' not in video_detail['itemInfo']:
                return None

            item = video_detail['itemInfo']['itemStruct']

            stats_data = item.get('stats', {})
            author = item.get('author', {})
            music = item.get('music', {})
            video_info = item.get('video', {})

            # Extract hashtags
            hashtags = []
            for tag in item.get('textExtra', []):
                if tag.get('hashtagName'):
                    hashtags.append(tag.get('hashtagName'))

            return {
                'thumbnail': video_info.get('cover') or video_info.get('dynamicCover'),
                'caption': item.get('desc', ''),
                'author_nickname': author.get('nickname'),
                'author_avatar': author.get('avatarLarger') or author.get('avatarMedium'),
                'author_id': author.get('id'),
                'views': stats_data.get('playCount', 0),
                'likes': stats_data.get('diggCount', 0),
                'comments': stats_data.get('commentCount', 0),
                'shares': stats_data.get('shareCount', 0),
                'bookmarks': stats_data.get('collectCount', 0),
                'music_id': music.get('id'),
                'music_title': music.get('title'),
                'music_author': music.get('authorName'),
                'hashtags': hashtags,
                'duration': video_info.get('duration'),
                'posted_at': datetime.fromtimestamp(item.get('createTime', 0)) if item.get('createTime') else None,
                'scraped_at': datetime.utcnow()
            }

        except Exception as e:
            print(f"  Error extracting stats: {e}")
            return None

    async def run_daily_update(self):
        """
        Main update function - runs through all videos and updates stats
        """
        print("🔄 Starting daily stats update...")
        print(f"⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

        db = SessionLocal()

        try:
            # Get all TikTok videos
            videos = db.query(Video).filter(Video.platform == 'tiktok').all()

            print(f"📊 Found {len(videos)} videos to update\n")

            updated_count = 0
            error_count = 0

            for idx, video in enumerate(videos, 1):
                print(f"[{idx}/{len(videos)}] Updating video {video.id}...")

                try:
                    # Fetch updated stats
                    stats = await self.update_video_stats(video.url)

                    if stats:
                        # Update video in database
                        for key, value in stats.items():
                            if value is not None:  # Only update if we got data
                                setattr(video, key, value)

                        db.commit()
                        updated_count += 1

                        print(f"  ✓ Updated - Views: {stats.get('views', 0):,}, Likes: {stats.get('likes', 0):,}")
                    else:
                        print(f"  ⚠️  Could not fetch stats")
                        error_count += 1

                    # Rate limiting - wait between requests
                    if idx < len(videos):
                        await asyncio.sleep(2)  # 2 second delay between videos

                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    error_count += 1

            # Update account stats after updating videos
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


async def main():
    """Run the daily update"""
    async with DailyStatsUpdater() as updater:
        await updater.run_daily_update()


if __name__ == "__main__":
    asyncio.run(main())
