#!/usr/bin/env python3
"""Test Instagram scraping functionality"""

import asyncio
import sys
sys.path.insert(0, '/Users/anubhavmishra/Desktop/social-media-tracker/backend')

from scrapers.url_scraper import URLScraper


async def test_instagram_profile():
    """Test scraping Instagram profiles"""

    profiles = [
        "https://www.instagram.com/piaprofessor/",
        "https://www.instagram.com/rose.studycorner/",
    ]

    async with URLScraper() as scraper:
        for profile_url in profiles:
            print(f"\n{'='*60}")
            print(f"Testing: {profile_url}")
            print(f"{'='*60}\n")

            try:
                result = await scraper.scrape_profile(profile_url, limit=5)

                print(f"\n✓ Profile Info:")
                print(f"  Username: {result['profile']['username']}")
                print(f"  Full Name: {result['profile']['nickname']}")
                print(f"  Followers: {result['profile']['follower_count']:,}")
                print(f"  Following: {result['profile']['following_count']:,}")
                print(f"  Total Posts: {result['profile']['post_count']:,}")
                print(f"  Bio: {result['profile']['bio'][:100]}..." if len(result['profile']['bio']) > 100 else f"  Bio: {result['profile']['bio']}")

                print(f"\n✓ Aggregate Stats:")
                print(f"  Total Posts Scraped: {result['aggregate_stats']['total_posts']}")
                print(f"  Total Videos: {result['aggregate_stats']['total_videos']}")
                print(f"  Total Likes: {result['aggregate_stats']['total_likes']:,}")
                print(f"  Total Comments: {result['aggregate_stats']['total_comments']:,}")
                print(f"  Avg Likes: {result['aggregate_stats']['avg_likes']:.0f}")

                print(f"\n✓ Sample Posts (showing first 3):")
                for i, post in enumerate(result['posts'][:3], 1):
                    print(f"\n  Post {i}:")
                    print(f"    Type: {'Video' if post['is_video'] else 'Photo'}")
                    print(f"    Likes: {post['likes']:,}")
                    print(f"    Comments: {post['comments']:,}")
                    if post['is_video']:
                        print(f"    Views: {post['views']:,}")
                        print(f"    Duration: {post['duration']:.1f}s")
                    print(f"    Caption: {post['caption'][:80]}..." if len(post['caption']) > 80 else f"    Caption: {post['caption']}")
                    print(f"    URL: {post['url']}")

                print(f"\n{'='*60}")
                print("✓ Test successful!")
                print(f"{'='*60}\n")

            except Exception as e:
                print(f"\n✗ Error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_instagram_profile())
