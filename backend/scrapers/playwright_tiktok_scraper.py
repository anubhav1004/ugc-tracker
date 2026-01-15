"""
TikTok Scraper using Playwright for browser automation
Handles JavaScript-rendered pages and anti-bot protection
"""

import asyncio
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from playwright.async_api import async_playwright


class PlaywrightTikTokScraper:
    """Scraper using Playwright browser automation"""

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

    def extract_username(self, url: str) -> str:
        """Extract username from TikTok URL"""
        if '@' in url:
            username = url.split('@')[1].split('/')[0].split('?')[0]
            return username
        return url

    async def scrape_video(self, url: str) -> Optional[Dict]:
        """
        Scrape a single video
        """
        try:
            page = await self.context.new_page()

            # Navigate to video page
            await page.goto(url, wait_until='networkidle', timeout=30000)

            # Wait a bit for dynamic content to load
            await page.wait_for_timeout(2000)

            # Extract page content
            content = await page.content()

            # Try to extract JSON data
            json_match = re.search(
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                content
            )

            await page.close()

            if not json_match:
                print(f"Could not find video data")
                return None

            page_data = json.loads(json_match.group(1))
            video_data = self._extract_video_from_page_data(page_data, url)

            return video_data

        except Exception as e:
            print(f"Error scraping video: {e}")
            return None

    def _extract_video_from_page_data(self, data: Dict, url: str) -> Optional[Dict]:
        """Extract video data from page JSON"""
        try:
            if '__DEFAULT_SCOPE__' not in data:
                return None

            default_scope = data['__DEFAULT_SCOPE__']

            # Look for video detail
            if 'webapp.video-detail' not in default_scope:
                return None

            video_detail = default_scope['webapp.video-detail']

            if 'itemInfo' not in video_detail or 'itemStruct' not in video_detail['itemInfo']:
                return None

            item = video_detail['itemInfo']['itemStruct']

            stats = item.get('stats', {})
            author = item.get('author', {})
            music = item.get('music', {})
            video_info = item.get('video', {})

            # Extract hashtags
            hashtags = []
            for tag in item.get('textExtra', []):
                if tag.get('hashtagName'):
                    hashtags.append(tag.get('hashtagName'))

            return {
                'id': item.get('id'),
                'platform': 'tiktok',
                'url': url,
                'thumbnail': video_info.get('cover') or video_info.get('dynamicCover'),
                'caption': item.get('desc', ''),
                'author_username': author.get('uniqueId'),
                'author_nickname': author.get('nickname'),
                'author_avatar': author.get('avatarLarger') or author.get('avatarMedium'),
                'author_id': author.get('id'),
                'views': stats.get('playCount', 0),
                'likes': stats.get('diggCount', 0),
                'comments': stats.get('commentCount', 0),
                'shares': stats.get('shareCount', 0),
                'bookmarks': stats.get('collectCount', 0),
                'music_id': music.get('id'),
                'music_title': music.get('title'),
                'music_author': music.get('authorName'),
                'music_url': None,
                'hashtags': hashtags,
                'mentions': [],
                'duration': video_info.get('duration'),
                'created_at': datetime.utcnow(),
                'posted_at': datetime.fromtimestamp(item.get('createTime', 0)) if item.get('createTime') else None,
                'scraped_at': datetime.utcnow()
            }

        except Exception as e:
            print(f"Error extracting video data: {e}")
            return None

    async def scrape_user_videos(self, profile_url: str, limit: int = 50) -> List[Dict]:
        """
        Scrape videos from a user profile
        """
        username = self.extract_username(profile_url)
        print(f"Scraping profile @{username}...")

        try:
            page = await self.context.new_page()

            # Navigate to profile page
            await page.goto(profile_url, wait_until='networkidle', timeout=30000)

            # Wait for content to load
            await page.wait_for_timeout(3000)

            # Scroll to load more videos
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(2000)

            # Extract page content
            content = await page.content()

            await page.close()

            # Try to extract JSON data
            json_match = re.search(
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                content
            )

            if not json_match:
                print(f"Could not find profile data")
                return []

            page_data = json.loads(json_match.group(1))

            # Extract video URLs
            video_urls = self._extract_video_urls_from_profile(page_data, username)

            print(f"Found {len(video_urls)} videos for @{username}")

            # Limit videos
            video_urls = video_urls[:limit]

            # Scrape each video
            videos = []
            for idx, video_url in enumerate(video_urls, 1):
                print(f"  [{idx}/{len(video_urls)}] Scraping video...")

                video_data = await self.scrape_video(video_url)

                if video_data:
                    videos.append(video_data)

                # Rate limiting
                if idx < len(video_urls):
                    await asyncio.sleep(1)

            print(f"✓ Successfully scraped {len(videos)} videos for @{username}")
            return videos

        except Exception as e:
            print(f"Error scraping profile @{username}: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _extract_video_urls_from_profile(self, data: Dict, username: str) -> List[str]:
        """Extract video URLs from profile page JSON"""
        urls = []

        try:
            if '__DEFAULT_SCOPE__' not in data:
                return urls

            default_scope = data['__DEFAULT_SCOPE__']

            # Check for user detail
            if 'webapp.user-detail' in default_scope:
                user_detail = default_scope['webapp.user-detail']

                # Look for itemList
                if 'itemList' in user_detail:
                    for item in user_detail['itemList']:
                        video_id = item.get('id')
                        if video_id:
                            url = f"https://www.tiktok.com/@{username}/video/{video_id}"
                            urls.append(url)

        except Exception as e:
            print(f"Error extracting video URLs: {e}")

        return urls


async def test():
    """Test the scraper"""
    async with PlaywrightTikTokScraper() as scraper:
        # Test profile scraping
        videos = await scraper.scrape_user_videos("https://www.tiktok.com/@therock", limit=5)
        print(f"\nGot {len(videos)} videos")

        if videos:
            video = videos[0]
            print(f"First video: {video['caption'][:50]}...")
            print(f"Views: {video['views']:,}")
            print(f"Likes: {video['likes']:,}")


if __name__ == "__main__":
    asyncio.run(test())
