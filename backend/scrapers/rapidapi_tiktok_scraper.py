"""
TikTok Scraper using RapidAPI
Uses tikwm TikTok Scraper API to bypass anti-bot protection
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
import os


class RapidAPITikTokScraper:
    """TikTok scraper using RapidAPI service"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize scraper with RapidAPI key
        Get your key from: https://rapidapi.com/tikwm-tikwm-default/api/tiktok-scraper7
        """
        # Try TikTok-specific key first, then fall back to general key
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY_TIKTOK') or os.getenv('RAPIDAPI_KEY')
        if not self.api_key:
            raise ValueError("RapidAPI key is required. Set RAPIDAPI_KEY_TIKTOK or RAPIDAPI_KEY environment variable or pass api_key parameter.")

        self.base_url = "https://tiktok-scraper7.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "tiktok-scraper7.p.rapidapi.com"
        }

    def extract_username(self, url: str) -> str:
        """Extract username from TikTok URL"""
        if '@' in url:
            username = url.split('@')[1].split('/')[0].split('?')[0]
            return username
        return url

    def get_user_posts(self, username: str, count: int = 10) -> List[Dict]:
        """
        Get posts from a user

        Args:
            username: TikTok username (without @)
            count: Number of posts to fetch (default 10, max 35)

        Returns:
            List of video data dictionaries
        """
        try:
            url = f"{self.base_url}/user/posts"
            params = {
                "unique_id": username,
                "count": min(count, 35)  # API max is 35
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('code') != 0:
                print(f"API Error: {data.get('msg', 'Unknown error')}")
                return []

            videos = []
            # The response has videos array directly in data
            video_list = data.get('data', {}).get('videos', [])

            for item in video_list:
                video_data = self._parse_video_data(item)
                if video_data:
                    videos.append(video_data)

            return videos

        except Exception as e:
            print(f"Error fetching user posts: {e}")
            return []

    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        Get detailed info for a specific video

        Args:
            video_url: Full TikTok video URL

        Returns:
            Video data dictionary
        """
        try:
            url = f"{self.base_url}/video/info"
            params = {"url": video_url}

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('code') != 0:
                print(f"API Error: {data.get('msg', 'Unknown error')}")
                return None

            item = data.get('data', {})
            return self._parse_video_data(item)

        except Exception as e:
            print(f"Error fetching video info: {e}")
            return None

    def _parse_video_data(self, item: Dict) -> Optional[Dict]:
        """Parse video data from API response"""
        try:
            # Extract basic info
            video_id = item.get('video_id') or item.get('aweme_id')
            if not video_id:
                return None

            # Get author info
            author = item.get('author', {})
            author_username = author.get('unique_id', '')
            if not author_username:
                author_username = author.get('uniqueId', '')

            # Get statistics (they're directly in the item, not nested)
            views = int(item.get('play_count', 0))
            likes = int(item.get('digg_count', 0))
            comments = int(item.get('comment_count', 0))
            shares = int(item.get('share_count', 0))
            bookmarks = int(item.get('collect_count', 0))

            # Get thumbnail
            thumbnail_url = item.get('cover') or item.get('origin_cover')

            # Get music info
            music_info = item.get('music_info', {})
            music_title = item.get('music') or music_info.get('title', '')

            # Get description
            title = item.get('title', '')

            # Extract hashtags from title
            import re
            hashtags = re.findall(r'#(\w+)', title)

            # Get create time
            create_time = item.get('create_time', 0)
            posted_at = None
            if create_time:
                try:
                    posted_at = datetime.fromtimestamp(int(create_time))
                except:
                    pass

            return {
                'id': str(video_id),
                'platform': 'tiktok',
                'url': f"https://www.tiktok.com/@{author_username}/video/{video_id}",
                'thumbnail': thumbnail_url,
                'caption': title,
                'author_username': author_username,
                'author_nickname': author.get('nickname', author_username),
                'author_avatar': author.get('avatar_thumb', {}).get('url_list', [None])[0] if isinstance(author.get('avatar_thumb'), dict) else None,
                'author_id': author.get('uid', ''),
                'views': views,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'bookmarks': bookmarks,
                'music_id': music_info.get('id'),
                'music_title': music_title,
                'music_author': music_info.get('author'),
                'music_url': None,
                'hashtags': hashtags,
                'mentions': [],
                'duration': item.get('duration'),
                'created_at': datetime.utcnow(),
                'posted_at': posted_at,
                'scraped_at': datetime.utcnow()
            }

        except Exception as e:
            print(f"Error parsing video data: {e}")
            import traceback
            traceback.print_exc()
            return None

    def scrape_profile(self, profile_url: str, limit: int = 10) -> Dict:
        """
        Scrape a TikTok profile

        Args:
            profile_url: TikTok profile URL
            limit: Number of videos to fetch (max 35)

        Returns:
            Dict with user info and videos
        """
        username = self.extract_username(profile_url)
        print(f"Fetching profile @{username} via RapidAPI...")

        videos = self.get_user_posts(username, count=limit)

        print(f"✓ Got {len(videos)} videos for @{username}")

        return {
            'username': username,
            'profile_url': profile_url,
            'videos': videos
        }


def test():
    """Test the scraper"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python rapidapi_tiktok_scraper.py <RAPIDAPI_KEY>")
        print("\nGet your key from: https://rapidapi.com/tikwm-tikwm-default/api/tiktok-scraper7")
        return

    api_key = sys.argv[1]
    scraper = RapidAPITikTokScraper(api_key=api_key)

    # Test with a known user
    print("Testing with @therock...")
    profile = scraper.scrape_profile("https://www.tiktok.com/@therock", limit=3)

    print(f"\nProfile: @{profile['username']}")
    print(f"Videos fetched: {len(profile['videos'])}")

    if profile['videos']:
        video = profile['videos'][0]
        print(f"\nFirst video:")
        print(f"  Caption: {video['caption'][:50]}...")
        print(f"  Views: {video['views']:,}")
        print(f"  Likes: {video['likes']:,}")
        print(f"  Comments: {video['comments']:,}")


if __name__ == "__main__":
    test()
