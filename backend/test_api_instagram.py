#!/usr/bin/env python3
"""Test Instagram integration via API"""

import requests
import json

API_URL = "http://localhost:8000"

def test_instagram_scraping():
    """Test scraping Instagram URLs via API"""

    # Test data
    instagram_urls = [
        "https://www.instagram.com/piaprofessor/",
        "https://www.instagram.com/rose.studycorner/",
    ]

    print("Testing Instagram URL scraping via API...")
    print(f"URLs to scrape: {instagram_urls}\n")

    # Make API request
    response = requests.post(
        f"{API_URL}/api/scrape/urls",
        json={"urls": instagram_urls},
        headers={"Content-Type": "application/json"}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Successfully scraped {len(data)} items!\n")

        for i, item in enumerate(data[:5], 1):  # Show first 5
            print(f"Item {i}:")
            print(f"  Platform: {item['platform']}")
            print(f"  Author: @{item['author_username']}")
            print(f"  Caption: {item['caption'][:60]}..." if len(item.get('caption', '')) > 60 else f"  Caption: {item.get('caption', '')}")
            print(f"  Views: {item['views']:,}")
            print(f"  Likes: {item['likes']:,}")
            print(f"  Comments: {item['comments']:,}")
            print(f"  URL: {item['url']}")
            print()

        print(f"✓ Test successful! API is working with Instagram.")

    else:
        print(f"\n✗ Error: {response.status_code}")
        print(f"Response: {response.text}")


if __name__ == "__main__":
    test_instagram_scraping()
