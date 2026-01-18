"""
Scrape ALL videos from max.curious1 and mari.curious profiles using pagination
"""

import sys
import os
import requests
from datetime import datetime
import time
import re

sys.path.insert(0, os.path.dirname(__file__))

# Set RapidAPI key
os.environ['RAPIDAPI_KEY'] = 'a4181840f6msh08a6c48170b4509p1be25cjsn5b0ce987b6e8'

from database import SessionLocal, Video

def fetch_all_videos_with_pagination(username):
    """Fetch all videos using pagination"""

    api_key = os.environ['RAPIDAPI_KEY']
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "tiktok-scraper7.p.rapidapi.com"
    }

    base_url = "https://tiktok-scraper7.p.rapidapi.com/user/posts"

    all_videos = []
    cursor = None
    page = 1

    print(f"Fetching videos with pagination...")

    while True:
        # Build params
        params = {
            "unique_id": username,
            "count": 35
        }

        # Add cursor if we have one
        if cursor:
            params['cursor'] = cursor

        print(f"  Page {page}: Fetching...", end=' ')

        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get('code') != 0:
                print(f"❌ Error: {data.get('msg', 'Unknown error')}")
                break

            # Get videos from this page
            videos = data.get('data', {}).get('videos', [])
            all_videos.extend(videos)

            print(f"Got {len(videos)} videos (Total: {len(all_videos)})")

            # Check if there are more pages
            has_more = data.get('data', {}).get('hasMore', False)
            cursor = data.get('data', {}).get('cursor')

            if not has_more or not cursor:
                print(f"  ✓ Reached end of profile")
                break

            # Increment page counter
            page += 1

            # Small delay between requests
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error: {e}")
            break

    return all_videos


def parse_video_data(item):
    """Parse video data from API response"""
    try:
        # Extract basic info
        video_id = item.get('video_id') or item.get('aweme_id')
        if not video_id:
            return None

        # Get author info
        author = item.get('author', {})
        author_username = author.get('unique_id', '') or author.get('uniqueId', '')

        # Get statistics
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
        print(f"Error parsing video: {e}")
        return None


def scrape_account(username, db):
    """Scrape a single account"""

    print(f"\n{'='*70}")
    print(f"Scraping @{username}")
    print(f"{'='*70}\n")

    # Check current count in database
    current_count = db.query(Video).filter(Video.author_username == username).count()
    print(f"Current videos in database: {current_count}\n")

    # Fetch all videos with pagination
    raw_videos = fetch_all_videos_with_pagination(username)

    if not raw_videos:
        print(f"❌ No videos fetched for @{username}")
        return

    # Parse videos
    print(f"\nParsing {len(raw_videos)} videos...")
    videos = []
    for raw_video in raw_videos:
        parsed = parse_video_data(raw_video)
        if parsed:
            videos.append(parsed)

    print(f"✓ Parsed {len(videos)} videos\n")

    # Save to database
    new_count = 0
    updated_count = 0

    print(f"Saving to database...")
    print(f"{'-'*70}\n")

    for i, video_data in enumerate(videos, 1):
        video_id = video_data['id']

        # Check if video already exists
        existing = db.query(Video).filter(Video.id == video_id).first()

        if existing:
            # Update existing video stats
            existing.views = video_data['views']
            existing.likes = video_data['likes']
            existing.comments = video_data['comments']
            existing.shares = video_data['shares']
            existing.bookmarks = video_data.get('bookmarks', 0)
            existing.scraped_at = datetime.utcnow()
            updated_count += 1
            status = "Updated"
        else:
            # Create new video
            video = Video(**video_data)
            db.add(video)
            new_count += 1
            status = "NEW"

        # Print new videos or every 10th video
        if status == "NEW" or i % 10 == 0:
            posted = video_data.get('posted_at', 'Unknown')
            print(f"[{i}/{len(videos)}] {status}: Posted {posted} - {video_data['views']:,} views")

    # Commit changes for this account
    db.commit()

    print(f"\n{'-'*70}")
    print(f"✅ @{username} Complete!")
    print(f"   New videos added: {new_count}")
    print(f"   Videos updated: {updated_count}")
    print(f"   Total processed: {len(videos)}")

    # Show final count
    final_count = db.query(Video).filter(Video.author_username == username).count()
    print(f"   Total in database: {final_count}")
    print(f"{'-'*70}")


def main():
    """Main scraping function"""

    accounts = [
        "max.curious1",
        "mari.curious"
    ]

    db = SessionLocal()

    try:
        print(f"\n{'#'*70}")
        print(f"# Scraping Max Curious and Mari Curious Accounts")
        print(f"{'#'*70}")

        for username in accounts:
            scrape_account(username, db)

            # Small delay between accounts
            time.sleep(2)

        print(f"\n{'#'*70}")
        print(f"# ALL ACCOUNTS SCRAPED SUCCESSFULLY!")
        print(f"{'#'*70}\n")

        # Summary
        print("FINAL SUMMARY:")
        print("="*70)
        for username in accounts:
            count = db.query(Video).filter(Video.author_username == username).count()
            print(f"  @{username}: {count} videos")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
