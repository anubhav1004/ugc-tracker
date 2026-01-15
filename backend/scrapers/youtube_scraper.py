from youtubesearchpython import VideosSearch, Hashtag
from typing import List, Dict
from datetime import datetime


class YouTubeScraper:
    """YouTube scraper using youtube-search-python"""

    def __init__(self):
        pass

    async def search_hashtag(self, hashtag: str, limit: int = 50) -> List[Dict]:
        """
        Search for videos by hashtag

        Args:
            hashtag: Hashtag name (without #)
            limit: Maximum number of videos to retrieve

        Returns:
            List of video dictionaries
        """
        videos = []

        try:
            # Use Hashtag class for hashtag search
            hashtag_search = Hashtag(f"#{hashtag}", limit=limit)
            results = hashtag_search.result()

            if 'result' in results:
                for video in results['result']:
                    video_data = self._parse_video(video)
                    videos.append(video_data)

        except Exception as e:
            print(f"Error searching YouTube hashtag {hashtag}: {e}")

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
        videos = []

        try:
            videos_search = VideosSearch(term, limit=limit)
            results = videos_search.result()

            if 'result' in results:
                for video in results['result']:
                    video_data = self._parse_video(video)
                    videos.append(video_data)

        except Exception as e:
            print(f"Error searching YouTube term {term}: {e}")

        return videos

    def _parse_video(self, video: Dict) -> Dict:
        """
        Parse YouTube video object into standardized format

        Args:
            video: YouTube API video object

        Returns:
            Standardized video dictionary
        """
        try:
            # Extract view count
            views = 0
            if 'viewCount' in video:
                view_count = video['viewCount']
                if isinstance(view_count, dict) and 'text' in view_count:
                    views = self._parse_count(view_count['text'])
                elif isinstance(view_count, str):
                    views = self._parse_count(view_count)

            # Extract duration
            duration = 0
            if 'duration' in video:
                duration_str = video.get('duration', '')
                duration = self._parse_duration(duration_str)

            return {
                "id": video.get('id', ''),
                "platform": "youtube",
                "url": video.get('link', ''),
                "thumbnail": video.get('thumbnails', [{}])[0].get('url', '') if video.get('thumbnails') else '',
                "caption": video.get('title', ''),

                # Author
                "author_username": video.get('channel', {}).get('name', ''),
                "author_nickname": video.get('channel', {}).get('name', ''),
                "author_avatar": video.get('channel', {}).get('thumbnails', [{}])[0].get('url', '') if video.get('channel', {}).get('thumbnails') else '',
                "author_id": video.get('channel', {}).get('id', ''),

                # Stats
                "views": views,
                "likes": 0,  # YouTube API doesn't provide likes in search results
                "comments": 0,
                "shares": 0,

                # Music (not applicable for YouTube)
                "music_id": "",
                "music_title": "",
                "music_author": "",
                "music_url": "",

                # Metadata
                "hashtags": [],  # Would need to parse from description
                "mentions": [],
                "duration": duration,

                # Timestamps
                "posted_at": self._parse_published_time(video.get('publishedTime', '')),
                "scraped_at": datetime.utcnow(),
            }

        except Exception as e:
            print(f"Error parsing YouTube video: {e}")
            return {
                "id": video.get('id', ''),
                "platform": "youtube",
                "url": video.get('link', ''),
                "scraped_at": datetime.utcnow(),
            }

    def _parse_count(self, count_str: str) -> int:
        """Parse view count string like '1.2M views' to integer"""
        try:
            count_str = count_str.replace(' views', '').replace(',', '').strip()

            if 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1_000_000)
            elif 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1_000)
            else:
                return int(count_str)

        except:
            return 0

    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string like '10:30' to seconds"""
        try:
            parts = duration_str.split(':')
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            return 0
        except:
            return 0

    def _parse_published_time(self, published_str: str) -> datetime:
        """Parse published time string like '2 days ago'"""
        # For now, return current time - would need more sophisticated parsing
        return datetime.utcnow()


async def test_youtube_scraper():
    """Test the YouTube scraper"""
    scraper = YouTubeScraper()

    print("Testing hashtag search...")
    videos = await scraper.search_hashtag("python", limit=5)
    print(f"Found {len(videos)} videos")

    if videos:
        print(f"First video: {videos[0]['caption'][:50]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_youtube_scraper())
