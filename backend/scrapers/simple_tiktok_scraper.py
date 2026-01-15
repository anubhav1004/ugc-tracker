"""
Simple TikTok Scraper using direct HTTP requests
Based on TikTok's web API patterns
"""

import httpx
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import asyncio


class SimpleTikTokScraper:
    """Simple scraper using direct HTTP requests to TikTok's web APIs"""

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

    def extract_username(self, url: str) -> str:
        """Extract username from TikTok URL"""
        if '@' in url:
            username = url.split('@')[1].split('/')[0].split('?')[0]
            return username
        return url

    async def scrape_video(self, url: str) -> Optional[Dict]:
        """
        Scrape a single video from TikTok
        Returns: Dict with video metadata
        """
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30.0) as client:
                # Get the page HTML
                response = await client.get(url)

                if response.status_code != 200:
                    print(f"Failed to fetch {url}: {response.status_code}")
                    return None

                html = response.text

                # Extract JSON data from the page
                json_match = re.search(
                    r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                    html
                )

                if not json_match:
                    print(f"Could not find video data in page")
                    return None

                page_data = json.loads(json_match.group(1))

                # Extract video data from the JSON structure
                video_data = self._extract_video_from_page_data(page_data, url)

                if video_data:
                    return video_data

                # Fallback: try OEmbed API
                return await self._fetch_from_oembed(url)

        except Exception as e:
            print(f"Error scraping video {url}: {e}")
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

            # Extract hashtags from textExtra
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
            print(f"Error extracting from page data: {e}")
            return None

    async def _fetch_from_oembed(self, url: str) -> Optional[Dict]:
        """Fallback: fetch basic info from OEmbed API"""
        try:
            oembed_url = f"https://www.tiktok.com/oembed?url={url}"

            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                response = await client.get(oembed_url)

                if response.status_code == 200:
                    data = response.json()

                    # Extract video ID from URL
                    video_id_match = re.search(r'/video/(\d+)', url)
                    video_id = video_id_match.group(1) if video_id_match else None

                    # Extract username from URL
                    username_match = re.search(r'@([\w.-]+)', url)
                    username = username_match.group(1) if username_match else None

                    return {
                        'id': video_id,
                        'platform': 'tiktok',
                        'url': url,
                        'thumbnail': data.get('thumbnail_url'),
                        'caption': data.get('title', ''),
                        'author_username': data.get('author_name', username),
                        'author_nickname': data.get('author_name'),
                        'author_avatar': None,
                        'author_id': None,
                        'views': 0,
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

        except Exception as e:
            print(f"OEmbed fetch failed: {e}")
            return None

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        if not text:
            return []
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags

    async def scrape_user_videos(self, profile_url: str, limit: int = 50) -> List[Dict]:
        """
        Scrape videos from a user profile by fetching their profile page
        and extracting video links
        """
        username = self.extract_username(profile_url)
        print(f"Scraping profile @{username}...")

        try:
            # Fetch profile page
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30.0) as client:
                response = await client.get(profile_url)

                if response.status_code != 200:
                    print(f"Failed to fetch profile: {response.status_code}")
                    return []

                html = response.text

                # Extract video URLs from the HTML
                video_urls = set()

                # Pattern 1: Find video links in the page
                video_links = re.findall(r'https://www\.tiktok\.com/@[\w.-]+/video/\d+', html)
                video_urls.update(video_links)

                # Pattern 2: Extract from JSON data if present
                json_match = re.search(
                    r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
                    html
                )

                if json_match:
                    try:
                        page_data = json.loads(json_match.group(1))
                        # Try to extract video list from page data
                        videos_from_json = self._extract_video_urls_from_page(page_data, username)
                        video_urls.update(videos_from_json)
                    except:
                        pass

                print(f"Found {len(video_urls)} video URLs for @{username}")

                # Limit to requested number
                video_urls = list(video_urls)[:limit]

                # Scrape each video
                videos = []
                for idx, video_url in enumerate(video_urls, 1):
                    print(f"  [{idx}/{len(video_urls)}] Scraping video...")

                    video_data = await self.scrape_video(video_url)

                    if video_data:
                        videos.append(video_data)

                    # Rate limiting: wait 1 second between requests
                    if idx < len(video_urls):
                        await asyncio.sleep(1)

                print(f"✓ Successfully scraped {len(videos)} videos for @{username}")
                return videos

        except Exception as e:
            print(f"Error scraping profile @{username}: {e}")
            return []

    def _extract_video_urls_from_page(self, data: Dict, username: str) -> List[str]:
        """Extract video URLs from profile page JSON data"""
        urls = []

        try:
            if '__DEFAULT_SCOPE__' in data:
                default_scope = data['__DEFAULT_SCOPE__']

                # Check for user detail with video list
                if 'webapp.user-detail' in default_scope:
                    user_detail = default_scope['webapp.user-detail']

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
    scraper = SimpleTikTokScraper()

    # Test single video
    video = await scraper.scrape_video("https://www.tiktok.com/@therock/video/7308033806571973930")
    if video:
        print(f"Video: {video['caption'][:50]}")
        print(f"Views: {video['views']:,}")
        print(f"Likes: {video['likes']:,}")

    # Test user profile
    # videos = await scraper.scrape_user_videos("https://www.tiktok.com/@therock", limit=5)
    # print(f"Got {len(videos)} videos")


if __name__ == "__main__":
    asyncio.run(test())
