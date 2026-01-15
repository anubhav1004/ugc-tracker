#!/usr/bin/env python3
"""Test Instagram scraping using RapidAPI"""

import sys
import os

sys.path.insert(0, '/Users/anubhavmishra/Desktop/social-media-tracker/backend')

from scrapers.rapidapi_instagram_scraper import RapidAPIInstagramScraper


def test_instagram_profiles():
    """Test scraping Instagram profiles"""

    # Get API key from environment or prompt
    api_key = os.getenv('RAPIDAPI_KEY')

    if not api_key:
        print("❌ RapidAPI key not found!")
        print("\nTo use Instagram scraping, you need a RapidAPI key:")
        print("1. Go to: https://rapidapi.com/restyler/api/instagram-scraper-api2")
        print("2. Subscribe to the API (free tier available)")
        print("3. Copy your API key")
        print("4. Add to .env file:")
        print("   RAPIDAPI_KEY=your_key_here")
        print("\nOr pass it as command line argument:")
        print(f"   python {sys.argv[0]} YOUR_API_KEY")
        return

    scraper = RapidAPIInstagramScraper(api_key=api_key)

    profiles = [
        "https://www.instagram.com/piaprofessor/",
        "https://www.instagram.com/rose.studycorner/",
    ]

    for profile_url in profiles:
        print(f"\n{'='*60}")
        print(f"Testing: {profile_url}")
        print(f"{'='*60}\n")

        try:
            result = scraper.scrape_profile(profile_url, limit=12)

            if not result['profile']:
                print(f"✗ Failed to fetch profile data")
                continue

            print(f"\n✓ Profile Info:")
            print(f"  Username: @{result['profile']['username']}")
            print(f"  Full Name: {result['profile']['nickname']}")
            print(f"  Followers: {result['profile']['follower_count']:,}")
            print(f"  Following: {result['profile']['following_count']:,}")
            print(f"  Total Posts: {result['profile']['post_count']:,}")
            print(f"  Verified: {'Yes' if result['profile']['is_verified'] else 'No'}")
            print(f"  Private: {'Yes' if result['profile']['is_private'] else 'No'}")

            if result['profile']['bio']:
                bio_preview = result['profile']['bio'][:100]
                if len(result['profile']['bio']) > 100:
                    bio_preview += "..."
                print(f"  Bio: {bio_preview}")

            print(f"\n✓ Aggregate Stats:")
            print(f"  Total Posts Scraped: {result['aggregate_stats']['total_posts']}")
            print(f"  Total Videos: {result['aggregate_stats']['total_videos']}")
            print(f"  Total Likes: {result['aggregate_stats']['total_likes']:,}")
            print(f"  Total Comments: {result['aggregate_stats']['total_comments']:,}")
            print(f"  Total Views (videos): {result['aggregate_stats']['total_views']:,}")
            print(f"  Avg Likes: {result['aggregate_stats']['avg_likes']:.0f}")
            print(f"  Avg Views: {result['aggregate_stats']['avg_views']:.0f}")

            print(f"\n✓ Sample Posts (showing first 3):")
            for i, post in enumerate(result['posts'][:3], 1):
                print(f"\n  Post {i}:")
                print(f"    Type: {'Video/Reel' if post['is_video'] else 'Photo'}")
                print(f"    Likes: {post['likes']:,}")
                print(f"    Comments: {post['comments']:,}")
                if post['is_video']:
                    print(f"    Views: {post['views']:,}")
                    print(f"    Duration: {post['duration']:.1f}s")

                caption_preview = post['caption'][:80]
                if len(post['caption']) > 80:
                    caption_preview += "..."
                print(f"    Caption: {caption_preview}")
                print(f"    URL: {post['url']}")

                if post['hashtags']:
                    print(f"    Hashtags: {', '.join(['#' + tag for tag in post['hashtags'][:5]])}")

            print(f"\n{'='*60}")
            print("✓ Test successful!")
            print(f"{'='*60}\n")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # Allow passing API key as command line argument
    if len(sys.argv) > 1:
        os.environ['RAPIDAPI_KEY'] = sys.argv[1]

    test_instagram_profiles()
