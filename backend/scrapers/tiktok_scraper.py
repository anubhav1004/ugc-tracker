import asyncio
import os
from typing import List, Dict, Optional
from datetime import datetime
from TikTokApi import TikTokApi


class TikTokScraper:
    """TikTok scraper using davidteather/TikTok-Api"""

    def __init__(self, ms_token: Optional[str] = None):
        self.ms_token = ms_token or os.getenv("TIKTOK_MS_TOKEN")
        self.api = None

    async def __aenter__(self):
        self.api = await TikTokApi().__aenter__()
        if self.ms_token:
            await self.api.create_sessions(
                ms_tokens=[self.ms_token],
                num_sessions=1,
                sleep_after=3
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.api:
            await self.api.__aexit__(exc_type, exc_val, exc_tb)

    async def search_hashtag(self, hashtag: str, limit: int = 50) -> List[Dict]:
        """
        Search for videos by hashtag

        Args:
            hashtag: Hashtag name (without #)
            limit: Maximum number of videos to retrieve

        Returns:
            List of video dictionaries
        """
        if not self.api:
            raise RuntimeError("API not initialized. Use 'async with' context manager.")

        videos = []
        try:
            async for video in self.api.hashtag(name=hashtag).videos(count=limit):
                video_data = await self._parse_video(video)
                videos.append(video_data)

                # Respect rate limits
                await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Error scraping hashtag {hashtag}: {e}")
            raise

        return videos

    async def search_term(self, term: str, limit: int = 50) -> List[Dict]:
        """
        Search for videos by search term

        Args:
            term: Search term
            limit: Maximum number of videos to retrieve

        Returns:
            List of video dictionaries
        """
        if not self.api:
            raise RuntimeError("API not initialized. Use 'async with' context manager.")

        videos = []
        try:
            async for video in self.api.search.videos(term, count=limit):
                video_data = await self._parse_video(video)
                videos.append(video_data)
                await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Error searching term {term}: {e}")
            raise

        return videos

    async def get_trending_videos(self, limit: int = 30) -> List[Dict]:
        """
        Get trending videos

        Args:
            limit: Maximum number of videos to retrieve

        Returns:
            List of video dictionaries
        """
        if not self.api:
            raise RuntimeError("API not initialized. Use 'async with' context manager.")

        videos = []
        try:
            async for video in self.api.trending.videos(count=limit):
                video_data = await self._parse_video(video)
                videos.append(video_data)
                await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Error getting trending videos: {e}")
            raise

        return videos

    async def _parse_video(self, video) -> Dict:
        """
        Parse TikTok video object into standardized format

        Args:
            video: TikTok API video object

        Returns:
            Standardized video dictionary
        """
        try:
            video_dict = video.as_dict

            # Extract hashtags
            hashtags = []
            if 'challenges' in video_dict:
                hashtags = [tag['title'] for tag in video_dict.get('challenges', [])]
            elif 'textExtra' in video_dict:
                hashtags = [
                    tag['hashtagName']
                    for tag in video_dict.get('textExtra', [])
                    if tag.get('hashtagName')
                ]

            # Extract mentions
            mentions = []
            if 'textExtra' in video_dict:
                mentions = [
                    tag['secUid']
                    for tag in video_dict.get('textExtra', [])
                    if tag.get('secUid') and not tag.get('hashtagName')
                ]

            return {
                "id": video_dict.get('id'),
                "platform": "tiktok",
                "url": f"https://www.tiktok.com/@{video_dict.get('author', {}).get('uniqueId', 'unknown')}/video/{video_dict.get('id')}",
                "thumbnail": video_dict.get('video', {}).get('cover', ''),
                "caption": video_dict.get('desc', ''),

                # Author
                "author_username": video_dict.get('author', {}).get('uniqueId', ''),
                "author_nickname": video_dict.get('author', {}).get('nickname', ''),
                "author_avatar": video_dict.get('author', {}).get('avatarThumb', ''),
                "author_id": video_dict.get('author', {}).get('id', ''),

                # Stats
                "views": video_dict.get('stats', {}).get('playCount', 0),
                "likes": video_dict.get('stats', {}).get('diggCount', 0),
                "comments": video_dict.get('stats', {}).get('commentCount', 0),
                "shares": video_dict.get('stats', {}).get('shareCount', 0),

                # Music
                "music_id": video_dict.get('music', {}).get('id', ''),
                "music_title": video_dict.get('music', {}).get('title', ''),
                "music_author": video_dict.get('music', {}).get('authorName', ''),
                "music_url": video_dict.get('music', {}).get('playUrl', ''),

                # Metadata
                "hashtags": hashtags,
                "mentions": mentions,
                "duration": video_dict.get('video', {}).get('duration', 0),

                # Timestamps
                "posted_at": datetime.fromtimestamp(video_dict.get('createTime', 0)),
                "scraped_at": datetime.utcnow(),
            }

        except Exception as e:
            print(f"Error parsing video: {e}")
            # Return minimal data
            return {
                "id": str(video_dict.get('id', '')),
                "platform": "tiktok",
                "url": "",
                "scraped_at": datetime.utcnow(),
            }


async def test_scraper():
    """Test the TikTok scraper"""
    async with TikTokScraper() as scraper:
        print("Testing hashtag search...")
        videos = await scraper.search_hashtag("travel", limit=5)
        print(f"Found {len(videos)} videos")
        if videos:
            print(f"First video: {videos[0]['caption'][:50]}...")


if __name__ == "__main__":
    asyncio.run(test_scraper())
