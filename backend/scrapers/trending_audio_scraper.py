import httpx
from typing import List, Dict, Optional
from datetime import datetime


class TrendingAudioScraper:
    """Scraper for TikTok trending audio/music"""

    def __init__(self, country: str = "US"):
        self.country = country
        self.proxies = self._get_country_proxy()

    def _get_country_proxy(self) -> Optional[Dict]:
        """Get proxy for specific country (if configured)"""
        # In production, you'd configure country-specific proxies
        # For now, return None (will use default)
        return None

    async def get_trending_audio(self, limit: int = 50) -> List[Dict]:
        """
        Get trending audio/music from TikTok

        Args:
            limit: Maximum number of trending audio to retrieve

        Returns:
            List of trending audio dictionaries
        """
        trending_audio = []

        try:
            async with httpx.AsyncClient(proxies=self.proxies, timeout=30.0) as client:
                # Try multiple TikTok discover endpoints
                endpoints = [
                    "https://www.tiktok.com/api/discover/music/",
                    "https://t.tiktok.com/api/discover/music/",
                    "https://m.tiktok.com/api/discover/music/",
                ]

                for endpoint in endpoints:
                    try:
                        response = await client.get(
                            endpoint,
                            headers={
                                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                                "Referer": "https://www.tiktok.com/",
                                "Accept": "application/json",
                            }
                        )

                        if response.status_code == 200:
                            data = response.json()
                            trending_audio = self._parse_trending_data(data, limit)
                            if trending_audio:
                                break

                    except Exception as e:
                        print(f"Error with endpoint {endpoint}: {e}")
                        continue

                # If API endpoints fail, try scraping from discovery page
                if not trending_audio:
                    trending_audio = await self._scrape_discovery_page(client, limit)

        except Exception as e:
            print(f"Error getting trending audio: {e}")

        return trending_audio[:limit]

    def _parse_trending_data(self, data: Dict, limit: int) -> List[Dict]:
        """Parse trending data from TikTok API response"""
        trending_audio = []

        try:
            # Handle different API response formats
            music_list = []

            if 'body' in data and isinstance(data['body'], list):
                # Format from ogohogo/tiktok-trending-data-api
                for section in data['body']:
                    if 'exploreList' in section:
                        for item in section['exploreList']:
                            if 'cardItem' in item:
                                card = item['cardItem']
                                if 'extraInfo' in card and 'playUrl' in card.get('extraInfo', {}):
                                    music_list.append(card)

            elif 'musicList' in data:
                # Alternative format
                music_list = data['musicList']

            # Parse music items
            for idx, music in enumerate(music_list[:limit]):
                try:
                    audio_data = {
                        "music_id": str(music.get('id', '')),
                        "platform": "tiktok",
                        "title": music.get('title', ''),
                        "author": music.get('description', '') or music.get('authorName', ''),
                        "play_url": self._extract_play_url(music),
                        "thumbnail": self._extract_thumbnail(music),
                        "total_videos": int(music.get('extraInfo', {}).get('posts', 0)) or int(music.get('videoCount', 0)),
                        "rank": idx + 1,
                        "country": self.country,
                        "trending_date": datetime.utcnow(),
                        "scraped_at": datetime.utcnow(),
                    }
                    trending_audio.append(audio_data)

                except Exception as e:
                    print(f"Error parsing music item: {e}")
                    continue

        except Exception as e:
            print(f"Error parsing trending data: {e}")

        return trending_audio

    def _extract_play_url(self, music: Dict) -> str:
        """Extract play URL from music object"""
        if 'extraInfo' in music and 'playUrl' in music['extraInfo']:
            play_urls = music['extraInfo']['playUrl']
            if isinstance(play_urls, list) and play_urls:
                return play_urls[0]
            return play_urls if isinstance(play_urls, str) else ''

        return music.get('playUrl', '')

    def _extract_thumbnail(self, music: Dict) -> str:
        """Extract thumbnail from music object"""
        if 'cover' in music:
            cover = music['cover']
            if isinstance(cover, dict):
                # Convert avatar format from ogohogo approach
                if 'uri' in cover:
                    uri = cover['uri']
                    return f"https://p16-sign-sg.tiktokcdn.com/tos-alisg-avt-0068/{uri}~c5_720x720.jpeg"
            elif isinstance(cover, str):
                return cover

        return music.get('coverThumb', '')

    async def _scrape_discovery_page(self, client: httpx.AsyncClient, limit: int) -> List[Dict]:
        """Fallback: scrape trending audio from TikTok discovery page"""
        trending_audio = []

        try:
            # This would use Playwright to scrape the page
            # For now, return empty list as fallback
            print("Discovery page scraping not implemented yet")

        except Exception as e:
            print(f"Error scraping discovery page: {e}")

        return trending_audio


async def test_trending_scraper():
    """Test the trending audio scraper"""
    scraper = TrendingAudioScraper(country="US")
    trending = await scraper.get_trending_audio(limit=10)

    print(f"Found {len(trending)} trending audio tracks")
    for idx, audio in enumerate(trending[:5], 1):
        print(f"{idx}. {audio['title']} by {audio['author']} - {audio['total_videos']} videos")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_trending_scraper())
