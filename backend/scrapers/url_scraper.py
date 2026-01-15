import asyncio
import re
from typing import Dict, Optional
from datetime import datetime
from TikTokApi import TikTokApi
import httpx
import os
from scrapers.rapidapi_instagram_scraper import RapidAPIInstagramScraper


class URLScraper:
    """Scrape video metrics from direct URLs"""

    def __init__(self, ms_token: Optional[str] = None, rapidapi_key: Optional[str] = None):
        self.ms_token = ms_token
        self.api = None
        self.rapidapi_key = rapidapi_key or os.getenv('RAPIDAPI_KEY')
        self.instagram_scraper = None
        if self.rapidapi_key:
            self.instagram_scraper = RapidAPIInstagramScraper(api_key=self.rapidapi_key)

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
            try:
                await self.api.__aexit__(exc_type, exc_val, exc_tb)
            except AttributeError:
                # TikTok API might not be fully initialized if we only used Instagram
                pass

    def detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        if 'tiktok.com' in url or 'vm.tiktok.com' in url:
            return 'tiktok'
        elif 'instagram.com' in url or 'instagr.am' in url:
            return 'instagram'
        elif 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'twitter'
        else:
            return 'unknown'

    def detect_url_type(self, url: str) -> str:
        """Detect if URL is profile or video"""
        # Strip query parameters for cleaner matching
        base_url = url.split('?')[0]

        # Profile patterns
        if re.search(r'tiktok\.com/@[\w\.-]+/?$', base_url):
            return 'profile'
        elif re.search(r'instagram\.com/[\w\.-]+/?$', base_url):
            return 'profile'
        elif re.search(r'youtube\.com/@[\w\.-]+/?$', base_url) or re.search(r'youtube\.com/c/[\w\.-]+/?$', base_url):
            return 'profile'

        # Video patterns
        elif re.search(r'tiktok\.com/@[\w\.-]+/video/\d+', base_url):
            return 'video'
        elif re.search(r'youtube\.com/watch\?v=', url) or re.search(r'youtu\.be/', base_url):
            return 'video'
        elif re.search(r'instagram\.com/(p|reel)/', base_url):
            return 'video'

        return 'unknown'

    async def scrape_url(self, url: str) -> Dict:
        """Scrape video from URL and return metrics"""
        platform = self.detect_platform(url)

        if platform == 'tiktok':
            return await self.scrape_tiktok_url(url)
        elif platform == 'youtube':
            return await self.scrape_youtube_url(url)
        elif platform == 'instagram':
            return await self.scrape_instagram_url(url)
        else:
            raise ValueError(f"Unsupported platform or invalid URL: {url}")

    async def scrape_profile(self, url: str, limit: int = 100) -> Dict:
        """
        Scrape all videos from a profile URL
        Returns: {videos: [], profile: {}, aggregate_stats: {}}
        """
        platform = self.detect_platform(url)
        url_type = self.detect_url_type(url)

        if url_type != 'profile':
            raise ValueError("URL must be a profile/account URL, not a video URL")

        if platform == 'tiktok':
            return await self.scrape_tiktok_profile(url, limit)
        elif platform == 'youtube':
            return await self.scrape_youtube_profile(url, limit)
        elif platform == 'instagram':
            return await self.scrape_instagram_profile(url, limit)
        else:
            raise ValueError(f"Unsupported platform or invalid URL: {url}")

    async def scrape_tiktok_url(self, url: str) -> Dict:
        """Scrape TikTok video from URL"""
        if not self.api:
            raise RuntimeError("API not initialized")

        try:
            # Extract video ID from URL
            video_id = self.extract_tiktok_id(url)
            if not video_id:
                raise ValueError("Could not extract TikTok video ID from URL")

            # Get video data
            video = self.api.video(id=video_id)
            video_data = await video.info()

            return self.parse_tiktok_video(video_data)

        except Exception as e:
            print(f"Error scraping TikTok URL: {e}")
            raise

    def extract_tiktok_id(self, url: str) -> Optional[str]:
        """Extract video ID from TikTok URL"""
        patterns = [
            r'tiktok\.com/@[\w\.-]+/video/(\d+)',
            r'tiktok\.com/v/(\d+)',
            r'vm\.tiktok\.com/(\w+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def parse_tiktok_video(self, video_dict: Dict) -> Dict:
        """Parse TikTok video data"""
        stats = video_dict.get('stats', {})
        author = video_dict.get('author', {})
        music = video_dict.get('music', {})
        video_info = video_dict.get('video', {})

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

        return {
            "id": str(video_dict.get('id', '')),
            "platform": "tiktok",
            "url": f"https://www.tiktok.com/@{author.get('uniqueId', 'unknown')}/video/{video_dict.get('id')}",
            "thumbnail": video_info.get('cover', ''),
            "caption": video_dict.get('desc', ''),

            # Author
            "author_username": author.get('uniqueId', ''),
            "author_nickname": author.get('nickname', ''),
            "author_avatar": author.get('avatarThumb', ''),
            "author_id": str(author.get('id', '')),

            # Metrics
            "views": int(stats.get('playCount', 0)),
            "likes": int(stats.get('diggCount', 0)),
            "comments": int(stats.get('commentCount', 0)),
            "shares": int(stats.get('shareCount', 0)),
            "bookmarks": int(stats.get('collectCount', 0)),  # TikTok bookmarks

            # Music
            "music_id": str(music.get('id', '')),
            "music_title": music.get('title', ''),
            "music_author": music.get('authorName', ''),

            # Metadata
            "hashtags": hashtags,
            "duration": video_info.get('duration', 0),
            "posted_at": datetime.fromtimestamp(video_dict.get('createTime', 0)),
            "scraped_at": datetime.utcnow(),
        }

    async def scrape_youtube_url(self, url: str) -> Dict:
        """Scrape YouTube video from URL"""
        try:
            video_id = self.extract_youtube_id(url)
            if not video_id:
                raise ValueError("Could not extract YouTube video ID")

            # Use YouTube Data API or scraping
            # For now, return basic structure
            async with httpx.AsyncClient() as client:
                # This would need YouTube API key or scraping implementation
                return {
                    "id": video_id,
                    "platform": "youtube",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "message": "YouTube scraping requires API key - feature coming soon"
                }

        except Exception as e:
            print(f"Error scraping YouTube URL: {e}")
            raise

    def extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)',
            r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    async def scrape_instagram_url(self, url: str) -> Dict:
        """Scrape Instagram post from URL using RapidAPI"""
        if not self.instagram_scraper:
            raise ValueError("RapidAPI key not configured for Instagram scraping")

        try:
            # Use RapidAPI scraper synchronously (it's not async)
            post_data = self.instagram_scraper.get_post_info(url)
            if not post_data:
                raise ValueError(f"Could not scrape Instagram post: {url}")

            return post_data

        except Exception as e:
            print(f"Error scraping Instagram URL: {e}")
            raise

    def extract_tiktok_username(self, url: str) -> Optional[str]:
        """Extract username from TikTok profile URL"""
        match = re.search(r'tiktok\.com/@([\w\.-]+)', url)
        if match:
            return match.group(1)
        return None

    async def scrape_tiktok_profile(self, url: str, limit: int = 100) -> Dict:
        """Scrape all videos from a TikTok profile"""
        if not self.api:
            raise RuntimeError("API not initialized")

        try:
            # Extract username from URL
            username = self.extract_tiktok_username(url)
            if not username:
                raise ValueError("Could not extract username from TikTok profile URL")

            # Get user object
            user = self.api.user(username=username)
            user_info = await user.info()

            # Get user's videos
            videos_data = []
            video_count = 0

            async for video in user.videos(count=limit):
                try:
                    parsed_video = self.parse_tiktok_video(video.as_dict)
                    videos_data.append(parsed_video)
                    video_count += 1
                    print(f"Scraped video {video_count}/{limit}: {parsed_video['id']}")
                except Exception as e:
                    print(f"Error parsing video: {e}")
                    continue

                if video_count >= limit:
                    break

            # Calculate aggregate statistics
            aggregate_stats = {
                "total_videos": len(videos_data),
                "total_views": sum(v["views"] for v in videos_data),
                "total_likes": sum(v["likes"] for v in videos_data),
                "total_comments": sum(v["comments"] for v in videos_data),
                "total_shares": sum(v["shares"] for v in videos_data),
                "total_bookmarks": sum(v.get("bookmarks", 0) for v in videos_data),
                "avg_views": sum(v["views"] for v in videos_data) / len(videos_data) if videos_data else 0,
                "avg_likes": sum(v["likes"] for v in videos_data) / len(videos_data) if videos_data else 0,
                "avg_engagement_rate": (
                    sum((v["likes"] + v["comments"] + v["shares"]) / max(v["views"], 1) for v in videos_data)
                    / len(videos_data) * 100 if videos_data else 0
                ),
            }

            # Extract profile info
            profile = {
                "username": user_info.get('uniqueId', username),
                "nickname": user_info.get('nickname', ''),
                "avatar": user_info.get('avatarThumb', ''),
                "bio": user_info.get('signature', ''),
                "follower_count": user_info.get('stats', {}).get('followerCount', 0),
                "following_count": user_info.get('stats', {}).get('followingCount', 0),
                "video_count": user_info.get('stats', {}).get('videoCount', 0),
                "likes_count": user_info.get('stats', {}).get('heartCount', 0),
            }

            return {
                "videos": videos_data,
                "profile": profile,
                "aggregate_stats": aggregate_stats,
            }

        except Exception as e:
            print(f"Error scraping TikTok profile: {e}")
            raise

    async def scrape_youtube_profile(self, url: str, limit: int = 100) -> Dict:
        """Scrape all videos from a YouTube channel"""
        # YouTube requires API key for channel video listing
        return {
            "videos": [],
            "profile": {},
            "aggregate_stats": {},
            "message": "YouTube profile scraping requires API key - feature coming soon"
        }

    async def scrape_instagram_profile(self, url: str, limit: int = 100) -> Dict:
        """Scrape all videos from an Instagram profile using RapidAPI"""
        if not self.instagram_scraper:
            raise ValueError("RapidAPI key not configured for Instagram scraping")

        try:
            # Use RapidAPI scraper synchronously (it's not async)
            profile_data = self.instagram_scraper.scrape_profile(url, limit=limit)

            return profile_data

        except Exception as e:
            print(f"Error scraping Instagram profile: {e}")
            raise


async def test_url_scraper():
    """Test the URL scraper"""
    test_url = "https://www.tiktok.com/@username/video/1234567890"

    async with URLScraper() as scraper:
        platform = scraper.detect_platform(test_url)
        print(f"Detected platform: {platform}")


if __name__ == "__main__":
    asyncio.run(test_url_scraper())
