"""
TikTok Statistics Scraper - No Video Download
Only scrapes metadata: views, likes, comments, shares, bookmarks, hashtags, captions
"""

import re
import json
import httpx
from typing import Dict, List, Optional
from datetime import datetime


class TikTokStatsScraper:
    """Lightweight TikTok scraper that only gets statistics"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from TikTok URL"""
        patterns = [
            r'/video/(\d+)',
            r'/v/(\d+)',
            r'tiktok\.com/t/(\w+)',
            r'vm\.tiktok\.com/(\w+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def extract_username(self, url: str) -> Optional[str]:
        """Extract username from TikTok URL"""
        match = re.search(r'@([\w.-]+)', url)
        if match:
            return match.group(1)
        return None

    async def scrape_video_stats(self, url: str) -> Dict:
        """
        Scrape video statistics from TikTok URL
        Returns: Dict with views, likes, comments, shares, bookmarks, caption, hashtags
        """

        video_id = self.extract_video_id(url)
        username = self.extract_username(url)

        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")

        try:
            # Method 1: Try OEmbed API (public, no auth needed)
            oembed_url = f"https://www.tiktok.com/oembed?url={url}"

            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30.0) as client:
                response = await client.get(oembed_url)

                if response.status_code == 200:
                    data = response.json()

                    # Extract info from oEmbed
                    result = {
                        'id': video_id,
                        'platform': 'tiktok',
                        'url': url,
                        'thumbnail': data.get('thumbnail_url'),
                        'caption': data.get('title', ''),
                        'author_username': data.get('author_name', username),
                        'author_nickname': data.get('author_name'),
                        'author_avatar': None,
                        'author_id': None,
                        'views': 0,  # oEmbed doesn't provide stats
                        'likes': 0,
                        'comments': 0,
                        'shares': 0,
                        'bookmarks': 0,
                        'music_id': None,
                        'music_title': None,
                        'music_author': None,
                        'music_url': None,
                        'hashtags': self._extract_hashtags(data.get('title', '')),
                        'mentions': [],
                        'duration': None,
                        'created_at': datetime.utcnow(),
                        'posted_at': None,
                        'scraped_at': datetime.utcnow()
                    }

                    # Try to get the full page to extract stats
                    try:
                        page_response = await client.get(url)
                        if page_response.status_code == 200:
                            html = page_response.text

                            # Try to extract JSON data from page
                            json_match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', html)
                            if json_match:
                                page_data = json.loads(json_match.group(1))

                                # Navigate the JSON structure to find video data
                                video_data = self._extract_from_page_data(page_data)
                                if video_data:
                                    result.update(video_data)

                    except Exception as page_error:
                        print(f"Could not extract stats from page: {page_error}")

                    return result

        except Exception as e:
            print(f"Error scraping video {url}: {e}")
            raise

        raise ValueError(f"Could not scrape video: {url}")

    def _extract_from_page_data(self, data: Dict) -> Optional[Dict]:
        """Extract video stats from page JSON data"""
        try:
            # TikTok page structure varies, try common paths
            if '__DEFAULT_SCOPE__' in data:
                default_scope = data['__DEFAULT_SCOPE__']

                # Look for video detail
                if 'webapp.video-detail' in default_scope:
                    video_detail = default_scope['webapp.video-detail']

                    if 'itemInfo' in video_detail and 'itemStruct' in video_detail['itemInfo']:
                        item = video_detail['itemInfo']['itemStruct']

                        stats = item.get('stats', {})
                        author = item.get('author', {})
                        music = item.get('music', {})

                        return {
                            'views': stats.get('playCount', 0),
                            'likes': stats.get('diggCount', 0),
                            'comments': stats.get('commentCount', 0),
                            'shares': stats.get('shareCount', 0),
                            'bookmarks': stats.get('collectCount', 0),
                            'author_id': author.get('id'),
                            'author_username': author.get('uniqueId'),
                            'author_nickname': author.get('nickname'),
                            'author_avatar': author.get('avatarLarger') or author.get('avatarMedium'),
                            'music_id': music.get('id'),
                            'music_title': music.get('title'),
                            'music_author': music.get('authorName'),
                            'caption': item.get('desc', ''),
                            'hashtags': [tag.get('name') for tag in item.get('textExtra', []) if tag.get('hashtagName')],
                            'duration': item.get('video', {}).get('duration'),
                            'posted_at': datetime.fromtimestamp(item.get('createTime', 0)) if item.get('createTime') else None,
                        }

        except Exception as e:
            print(f"Error extracting from page data: {e}")

        return None

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from caption"""
        if not text:
            return []

        hashtags = re.findall(r'#(\w+)', text)
        return hashtags

    async def scrape_profile_videos(self, profile_url: str, limit: int = 50) -> List[Dict]:
        """
        Scrape video list from profile (gets URLs, then scrapes each video's stats)
        """

        username = self.extract_username(profile_url)
        if not username:
            raise ValueError(f"Could not extract username from URL: {profile_url}")

        try:
            # For now, return placeholder
            # Full profile scraping requires more complex auth
            print(f"Profile scraping for @{username} requires TikTok auth token")
            return []

        except Exception as e:
            print(f"Error scraping profile {profile_url}: {e}")
            return []

    async def scrape_video_by_url(self, url: str) -> Dict:
        """Main method to scrape a single video's statistics"""
        return await self.scrape_video_stats(url)


# Alternative: TikTok API v2 (Unofficial) approach
class TikTokAPIv2Scraper:
    """Uses TikTok's unofficial API endpoints"""

    def __init__(self):
        self.base_url = "https://api16-normal-c-useast1a.tiktokv.com"
        self.headers = {
            'User-Agent': 'com.zhiliaoapp.musically/2022600040 (Linux; U; Android 10; en_US; Pixel 4; Build/QQ3A.200805.001; Cronet/TTNetVersion:b4a9b5c8 2021-12-16 QuicVersion:47946b2e 2021-12-07)',
        }

    async def get_video_info(self, video_id: str) -> Dict:
        """Get video info from TikTok API"""

        params = {
            'aweme_id': video_id,
            'aid': '1988',
            'app_name': 'musical_ly',
            'device_platform': 'android',
        }

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/aweme/v1/feed/",
                    params=params
                )

                if response.status_code == 200:
                    data = response.json()

                    if 'aweme_list' in data and len(data['aweme_list']) > 0:
                        item = data['aweme_list'][0]

                        stats = item.get('statistics', {})
                        author = item.get('author', {})
                        music = item.get('music', {})

                        return {
                            'id': video_id,
                            'platform': 'tiktok',
                            'url': f"https://www.tiktok.com/@{author.get('unique_id')}/video/{video_id}",
                            'thumbnail': item.get('video', {}).get('cover', {}).get('url_list', [None])[0],
                            'caption': item.get('desc', ''),
                            'author_username': author.get('unique_id'),
                            'author_nickname': author.get('nickname'),
                            'author_avatar': author.get('avatar_larger', {}).get('url_list', [None])[0],
                            'author_id': author.get('uid'),
                            'views': stats.get('play_count', 0),
                            'likes': stats.get('digg_count', 0),
                            'comments': stats.get('comment_count', 0),
                            'shares': stats.get('share_count', 0),
                            'bookmarks': stats.get('collect_count', 0),
                            'music_id': music.get('id'),
                            'music_title': music.get('title'),
                            'music_author': music.get('author'),
                            'hashtags': [tag.get('hashtag_name') for tag in item.get('text_extra', []) if 'hashtag_name' in tag],
                            'duration': item.get('video', {}).get('duration'),
                            'posted_at': datetime.fromtimestamp(item.get('create_time', 0)) if item.get('create_time') else None,
                            'scraped_at': datetime.utcnow()
                        }

        except Exception as e:
            print(f"Error using TikTok API v2: {e}")

        return None
