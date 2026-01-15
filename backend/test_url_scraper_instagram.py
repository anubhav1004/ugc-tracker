#!/usr/bin/env python3
"""Test URLScraper with Instagram directly (no API/database needed)"""

import asyncio
import sys
import os

sys.path.insert(0, '/Users/anubhavmishra/Desktop/social-media-tracker/backend')

from scrapers.url_scraper import URLScraper


async def test_instagram_urlscraper():
    """Test Instagram scraping via URLScraper"""

    instagram_urls = [
        "https://www.instagram.com/piaprofessor/",
        "https://www.instagram.com/rose.studycorner/",
    ]

    print("Testing Instagram via URLScraper...")
    print(f"RAPIDAPI_KEY loaded: {bool(os.getenv('RAPIDAPI_KEY'))}\n")

    async with URLScraper(rapidapi_key=os.getenv('RAPIDAPI_KEY')) as scraper:
        for url in instagram_urls:
            print(f"\n{'='*60}")
            print(f"Scraping: {url}")
            print(f"{'='*60}\n")

            try:
                # Detect URL type
                url_type = scraper.detect_url_type(url)
                print(f"URL Type: {url_type}")

                if url_type == 'profile':
                    # Scrape profile
                    result = await scraper.scrape_profile(url, limit=5)

                    print(f"\n✓ Profile scraped successfully!")
                    print(f"  Username: @{result['profile']['username']}")
                    print(f"  Full Name: {result['profile']['nickname']}")
                    print(f"  Followers: {result['profile']['follower_count']:,}")
                    print(f"  Posts scraped: {len(result['posts'])}")
                    print(f"  Videos: {len(result['videos'])}")

                    if result['posts']:
                        print(f"\n  First post:")
                        post = result['posts'][0]
                        print(f"    Type: {'Video' if post['is_video'] else 'Photo'}")
                        print(f"    Likes: {post['likes']:,}")
                        print(f"    Views: {post['views']:,}")
                        print(f"    URL: {post['url']}")

            except Exception as e:
                print(f"\n✗ Error: {e}")
                import traceback
                traceback.print_exc()

    print(f"\n{'='*60}")
    print("✓ Test complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(test_instagram_urlscraper())
