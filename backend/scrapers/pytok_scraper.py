"""
TikTok Scraper using pytok library
Scrapes user profiles and videos without downloading video files
"""

import asyncio
from typing import Dict, List
from datetime import datetime
from pytok.tiktok import PyTok


class PyTokScraper:
    """Scraper using pytok library for TikTok user profiles and videos"""

    def __init__(self):
        self.api = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.api = PyTok(request_delay=2)  # 2 second delay between requests
        await self.api.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.api:
            await self.api.__aexit__(exc_type, exc_val, exc_tb)

    def extract_username(self, url: str) -> str:
        """Extract username from TikTok URL"""
        if '@' in url:
            username = url.split('@')[1].split('/')[0].split('?')[0]
            return username
        return url

    async def scrape_profile(self, profile_url: str, limit: int = 50) -> Dict:
        """
        Scrape user profile and their videos
        Returns: Dict with user info and list of videos
        """
        username = self.extract_username(profile_url)

        print(f"Fetching profile for @{username}...")

        try:
            # Get user object
            user = self.api.user(username=username)

            # Get user profile info
            try:
                user_data = await user.info()
                print(f"✓ Got profile info for @{username}")
            except Exception as e:
                print(f"✗ Could not get profile info: {e}")
                user_data = {}

            # Get user videos
            videos = []
            video_count = 0

            print(f"Fetching videos for @{username}...")
            async for video in user.videos():
                if video_count >= limit:
                    break

                try:
                    video_info = video.info()

                    # Extract the fields we need
                    video_data = self._parse_video_info(video_info, username)
                    videos.append(video_data)
                    video_count += 1

                    if video_count % 10 == 0:
                        print(f"  Fetched {video_count} videos...")

                except Exception as e:
                    print(f"  Error fetching video: {e}")
                    continue

            print(f"✓ Fetched {len(videos)} videos for @{username}")

            return {
                'username': username,
                'profile_url': profile_url,
                'user_info': user_data,
                'videos': videos
            }

        except Exception as e:
            print(f"✗ Error scraping profile @{username}: {e}")
            raise

    def _parse_video_info(self, video_info: Dict, username: str) -> Dict:
        """Parse pytok video info into our schema"""

        # pytok returns nested dict with video metadata
        video_id = video_info.get('video_id', '')
        author_name = video_info.get('author_name', username)
        author_id = video_info.get('author_id', '')
        desc = video_info.get('desc', '')
        hashtags = video_info.get('hashtags', [])

        # Stats
        digg_count = video_info.get('digg_count', 0)
        share_count = video_info.get('share_count', 0)
        comment_count = video_info.get('comment_count', 0)
        play_count = video_info.get('play_count', 0)

        # Create timestamp
        createtime = video_info.get('createtime')
        if createtime:
            try:
                posted_at = datetime.strptime(createtime, '%Y-%m-%d %H:%M:%S')
            except:
                posted_at = None
        else:
            posted_at = None

        # Build URL
        url = f"https://www.tiktok.com/@{author_name}/video/{video_id}"

        return {
            'id': video_id,
            'platform': 'tiktok',
            'url': url,
            'thumbnail': None,  # pytok doesn't provide thumbnails in info()
            'caption': desc,
            'author_username': author_name,
            'author_nickname': author_name,
            'author_avatar': None,
            'author_id': author_id,
            'views': play_count,
            'likes': digg_count,
            'comments': comment_count,
            'shares': share_count,
            'bookmarks': 0,  # pytok doesn't provide bookmark count
            'music_id': None,
            'music_title': None,
            'music_author': None,
            'music_url': None,
            'hashtags': hashtags,
            'mentions': video_info.get('mentions', []),
            'duration': None,
            'created_at': datetime.utcnow(),
            'posted_at': posted_at,
            'scraped_at': datetime.utcnow()
        }

    async def scrape_video_by_url(self, url: str) -> Dict:
        """Scrape a single video by URL"""
        # pytok is designed for bulk profile scraping, not single videos
        # For single videos, we'll need to use a different approach
        raise NotImplementedError("Single video scraping not supported with pytok")


async def test_scraper():
    """Test the scraper with one account"""
    async with PyTokScraper() as scraper:
        profile = await scraper.scrape_profile("https://www.tiktok.com/@therock", limit=5)
        print(f"\nProfile: @{profile['username']}")
        print(f"Videos fetched: {len(profile['videos'])}")

        if profile['videos']:
            video = profile['videos'][0]
            print(f"\nFirst video:")
            print(f"  ID: {video['id']}")
            print(f"  Caption: {video['caption'][:50]}...")
            print(f"  Views: {video['views']:,}")
            print(f"  Likes: {video['likes']:,}")


if __name__ == "__main__":
    asyncio.run(test_scraper())
