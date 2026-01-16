"""
Instagram Scraper using RapidAPI
Uses Instagram Bulk Profile Scraper API - more reliable and feature-rich
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
import os


class RapidAPIInstagramScraper:
    """Instagram scraper using RapidAPI service"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize scraper with RapidAPI key
        Uses instagram-social API
        """
        # Try Instagram-specific key first, then fall back to general key
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY_INSTAGRAM') or os.getenv('RAPIDAPI_KEY')
        if not self.api_key:
            raise ValueError("RapidAPI key is required. Set RAPIDAPI_KEY_INSTAGRAM or RAPIDAPI_KEY environment variable or pass api_key parameter.")

        self.base_url = "https://instagram-social.p.rapidapi.com/api/v1/instagram"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "instagram-social.p.rapidapi.com"
        }

    def extract_username(self, url: str) -> str:
        """Extract username from Instagram URL"""
        # Remove trailing slash
        url = url.rstrip('/')

        # Handle different Instagram URL formats
        if 'instagram.com/' in url:
            parts = url.split('instagram.com/')
            if len(parts) > 1:
                username = parts[1].split('/')[0].split('?')[0]
                return username
        return url

    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Get user profile information

        Args:
            username: Instagram username (without @)

        Returns:
            User profile data dictionary
        """
        try:
            url = f"{self.base_url}/profile"
            params = {"username": username}

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            print(f"RapidAPI Response Status: {response.status_code}")
            response.raise_for_status()

            data = response.json()
            print(f"RapidAPI Response Data: {data}")

            if not data or 'body' not in data:
                print(f"No profile data found for @{username}")
                print(f"Response keys: {list(data.keys()) if data else 'No data'}")
                return None

            profile = data['body']

            return {
                'username': profile.get('username', username),
                'nickname': profile.get('full_name', username),
                'avatar': profile.get('profile_pic', ''),
                'bio': profile.get('biography', ''),
                'follower_count': profile.get('followers', 0),
                'following_count': profile.get('following', 0),
                'post_count': profile.get('posts', 0),
                'is_verified': profile.get('is_verified', False),
                'is_private': profile.get('is_private', False),
            }

        except Exception as e:
            print(f"Error fetching user info: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_user_posts(self, username: str, count: int = 12) -> List[Dict]:
        """
        Get posts from a user

        Args:
            username: Instagram username (without @)
            count: Number of posts to fetch (default 12)

        Returns:
            List of post data dictionaries
        """
        try:
            url = f"{self.base_url}/posts"
            params = {"username": username}

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if not data or 'body' not in data:
                print(f"No posts found for @{username}")
                return []

            posts = []
            items = data.get('body', [])[:count]

            for item in items:
                post_data = self._parse_post_data(item, username)
                if post_data:
                    posts.append(post_data)

            return posts

        except Exception as e:
            print(f"Error fetching user posts: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_post_info(self, post_url: str) -> Optional[Dict]:
        """
        Get detailed info for a specific post

        Args:
            post_url: Full Instagram post URL or shortcode

        Returns:
            Post data dictionary
        """
        try:
            # Extract shortcode from URL
            import re
            match = re.search(r'/p/([A-Za-z0-9_-]+)', post_url)
            if match:
                code = match.group(1)
            else:
                code = post_url

            url = f"{self.base_url}/post"
            params = {"code": code}

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if not data or 'data' not in data:
                print(f"No post data found")
                return None

            item = data.get('data', {})
            username = item.get('owner', {}).get('username', 'unknown')

            return self._parse_post_data(item, username)

        except Exception as e:
            print(f"Error fetching post info: {e}")
            return None

    def _parse_post_data(self, item: Dict, username: str) -> Optional[Dict]:
        """Parse post data from API response"""
        try:
            # Extract basic info
            post_id = item.get('id')
            if not post_id:
                return None

            shortcode = item.get('shortcode', '')

            # Get owner info
            user = item.get('user', {})
            author_username = user.get('username', username)

            # Get media type and check if it's a video
            media_type = item.get('media_type', 0)
            product_type = item.get('product_type', '')
            # media_type: 1=photo, 2=video, 8=carousel
            # product_type: 'feed', 'igtv', 'clips' (reels)
            is_video = media_type == 2 or product_type in ['clips', 'igtv']

            # Get statistics
            likes = int(item.get('like_count', 0))
            comments = int(item.get('comment_count', 0))
            # play_count can be ig_play_count or fb_play_count
            views = int(item.get('play_count', 0) or item.get('ig_play_count', 0) or item.get('fb_play_count', 0))

            # Get thumbnail
            thumbnail_url = item.get('thumbnail_url') or item.get('media_url')

            # Get caption
            caption = item.get('caption', '') or ''

            # Extract hashtags from caption
            import re
            hashtags = re.findall(r'#(\w+)', caption) if caption else []

            # Get create time
            taken_at = item.get('taken_at', 0)
            posted_at = None
            if taken_at:
                try:
                    posted_at = datetime.fromtimestamp(int(taken_at))
                except:
                    pass

            # Get video duration - not provided in this API
            duration = 0

            # Get permalink
            permalink = item.get('permalink', f"https://www.instagram.com/p/{shortcode}/")

            return {
                'id': str(shortcode) if shortcode else str(post_id),
                'platform': 'instagram',
                'url': permalink,
                'thumbnail': thumbnail_url,
                'caption': caption,
                'author_username': author_username,
                'author_nickname': user.get('full_name', author_username),
                'author_avatar': user.get('profile_pic', ''),
                'author_id': str(user.get('id', '')),
                'views': views,
                'likes': likes,
                'comments': comments,
                'shares': int(item.get('reshare_count', 0)),  # This API provides reshare count!
                'bookmarks': 0,  # Not available
                'hashtags': hashtags,
                'duration': duration,
                'posted_at': posted_at,
                'scraped_at': datetime.utcnow(),
                '_is_video': is_video  # Internal flag for filtering, not saved to DB
            }

        except Exception as e:
            print(f"Error parsing post data: {e}")
            import traceback
            traceback.print_exc()
            return None

    def scrape_profile(self, profile_url: str, limit: int = 12) -> Dict:
        """
        Scrape an Instagram profile

        Args:
            profile_url: Instagram profile URL
            limit: Number of posts to fetch

        Returns:
            Dict with user info and posts
        """
        username = self.extract_username(profile_url)
        print(f"Fetching profile @{username} via RapidAPI...")

        # Get profile info
        profile_info = self.get_user_info(username)
        if not profile_info:
            print(f"Failed to get profile info for @{username}")
            return {
                'username': username,
                'profile': {},
                'videos': [],
                'posts': [],
                'aggregate_stats': {}
            }

        # Get posts
        posts = self.get_user_posts(username, count=limit)

        print(f"✓ Got {len(posts)} posts for @{username}")

        # Separate videos from all posts (check internal flag)
        videos = [p for p in posts if p.get('_is_video', False)]

        # Calculate aggregate stats
        aggregate_stats = {
            'total_videos': len(videos),
            'total_posts': len(posts),
            'total_views': sum(p.get('views', 0) for p in videos),
            'total_likes': sum(p.get('likes', 0) for p in posts),
            'total_comments': sum(p.get('comments', 0) for p in posts),
            'total_shares': 0,
            'total_bookmarks': 0,
            'avg_views': sum(p.get('views', 0) for p in videos) / len(videos) if videos else 0,
            'avg_likes': sum(p.get('likes', 0) for p in posts) / len(posts) if posts else 0,
            'avg_engagement_rate': (
                sum((p['likes'] + p['comments']) / max(p.get('views', 1), 1) for p in videos)
                / len(videos) * 100 if videos else 0
            ),
        }

        return {
            'username': username,
            'profile': profile_info,
            'videos': videos,
            'posts': posts,
            'aggregate_stats': aggregate_stats
        }


def test():
    """Test the scraper"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python rapidapi_instagram_scraper.py <RAPIDAPI_KEY>")
        print("\nGet your key from: https://rapidapi.com/restyler/api/instagram-scraper-api2")
        return

    api_key = sys.argv[1]
    scraper = RapidAPIInstagramScraper(api_key=api_key)

    # Test with a known user
    print("Testing with @instagram...")
    profile = scraper.scrape_profile("https://www.instagram.com/instagram/", limit=5)

    print(f"\nProfile: @{profile['username']}")
    print(f"Full Name: {profile['profile'].get('nickname', 'N/A')}")
    print(f"Followers: {profile['profile'].get('follower_count', 0):,}")
    print(f"Posts fetched: {len(profile['posts'])}")
    print(f"Videos: {len(profile['videos'])}")

    if profile['posts']:
        post = profile['posts'][0]
        print(f"\nFirst post:")
        print(f"  Type: {'Video' if post['is_video'] else 'Photo'}")
        print(f"  Caption: {post['caption'][:50]}...")
        print(f"  Likes: {post['likes']:,}")
        print(f"  Comments: {post['comments']:,}")
        if post['is_video']:
            print(f"  Views: {post['views']:,}")


if __name__ == "__main__":
    test()
