"""
Lightweight TikTok Profile Scraper
Only scrapes the last 2 videos from each profile to avoid anti-bot detection
"""

import asyncio
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from playwright.async_api import async_playwright


class LightweightProfileScraper:
    """Scrapes only the last 2 videos from TikTok profiles"""

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

    async def scrape_profile_light(self, profile_url: str) -> Dict:
        """
        Lightweight profile scrape - only last 2 videos
        Returns: Dict with profile info and last 2 videos
        """
        username = self.extract_username(profile_url)
        print(f"Fetching profile @{username} (last 2 videos only)...")

        try:
            page = await self.context.new_page()

            # Navigate to profile page
            print(f"  Loading profile page...")
            await page.goto(profile_url, wait_until='domcontentloaded', timeout=45000)

            # Wait for content to load
            await page.wait_for_timeout(4000)

            # Extract page content
            content = await page.content()

            await page.close()

            # Try to extract JSON data
            json_match = re.search(
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                content
            )

            if not json_match:
                print(f"  ✗ Could not find profile data")
                return {
                    'username': username,
                    'profile_url': profile_url,
                    'followers': 0,
                    'videos': []
                }

            page_data = json.loads(json_match.group(1))

            # Extract profile info and videos
            profile_info, video_urls = self._extract_profile_data(page_data, username)

            # Only take last 2 videos
            video_urls = video_urls[:2]

            print(f"  ✓ Found {len(video_urls)} recent videos")

            # Scrape each video (lightweight - just from page data, no extra requests)
            videos = []
            for video_url in video_urls:
                video_data = self._extract_video_from_url(video_url, username)
                if video_data:
                    videos.append(video_data)

            result = {
                'username': username,
                'profile_url': profile_url,
                'followers': profile_info.get('followers', 0),
                'videos': videos
            }

            print(f"  ✓ Scraped @{username}: {profile_info.get('followers', 0):,} followers, {len(videos)} videos")
            return result

        except Exception as e:
            print(f"  ✗ Error scraping profile @{username}: {e}")
            import traceback
            traceback.print_exc()
            return {
                'username': username,
                'profile_url': profile_url,
                'followers': 0,
                'videos': []
            }

    def _extract_profile_data(self, data: Dict, username: str) -> tuple:
        """Extract profile info and video URLs from page JSON"""
        profile_info = {'followers': 0}
        video_urls = []

        try:
            if '__DEFAULT_SCOPE__' not in data:
                return profile_info, video_urls

            default_scope = data['__DEFAULT_SCOPE__']

            # Check for user detail
            if 'webapp.user-detail' in default_scope:
                user_detail = default_scope['webapp.user-detail']

                # Get follower count
                if 'userInfo' in user_detail and 'stats' in user_detail['userInfo']:
                    stats = user_detail['userInfo']['stats']
                    profile_info['followers'] = stats.get('followerCount', 0)

                # Get video list
                if 'itemList' in user_detail:
                    for item in user_detail['itemList']:
                        video_id = item.get('id')
                        if video_id:
                            url = f"https://www.tiktok.com/@{username}/video/{video_id}"
                            video_urls.append(url)

        except Exception as e:
            print(f"  Error extracting profile data: {e}")

        return profile_info, video_urls

    def _extract_video_from_url(self, url: str, username: str) -> Optional[Dict]:
        """
        Create basic video record from URL
        Full stats will be fetched later by the daily update job
        """
        # Extract video ID
        video_id_match = re.search(r'/video/(\d+)', url)
        if not video_id_match:
            return None

        video_id = video_id_match.group(1)

        return {
            'id': video_id,
            'platform': 'tiktok',
            'url': url,
            'thumbnail': None,
            'caption': None,
            'author_username': username,
            'author_nickname': username,
            'author_avatar': None,
            'author_id': None,
            'views': 0,  # Will be updated by daily scraper
            'likes': 0,  # Will be updated by daily scraper
            'comments': 0,  # Will be updated by daily scraper
            'shares': 0,  # Will be updated by daily scraper
            'bookmarks': 0,  # Will be updated by daily scraper
            'music_id': None,
            'music_title': None,
            'music_author': None,
            'music_url': None,
            'hashtags': [],
            'mentions': [],
            'duration': None,
            'created_at': datetime.utcnow(),
            'posted_at': None,
            'scraped_at': datetime.utcnow()
        }


async def test():
    """Test the lightweight scraper"""
    async with LightweightProfileScraper() as scraper:
        # Test with one profile
        profile = await scraper.scrape_profile_light("https://www.tiktok.com/@therock")

        print(f"\n{'='*60}")
        print(f"Profile: @{profile['username']}")
        print(f"Followers: {profile['followers']:,}")
        print(f"Videos found: {len(profile['videos'])}")

        if profile['videos']:
            for i, video in enumerate(profile['videos'], 1):
                print(f"\nVideo {i}:")
                print(f"  ID: {video['id']}")
                print(f"  URL: {video['url']}")
        print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(test())
