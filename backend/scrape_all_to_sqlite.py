"""
Scrape ALL videos from all three accounts and save to SQLite
"""

import sys
import os
import requests
from datetime import datetime
import time
import re

sys.path.insert(0, os.path.dirname(__file__))

# Force SQLite usage
os.environ['DATABASE_URL'] = 'sqlite:///social_media_tracker.db'
os.environ['RAPIDAPI_KEY'] = 'a4181840f6msh08a6c48170b4509p1be25cjsn5b0ce987b6e8'

from database import SessionLocal, Video

def fetch_all_videos_with_pagination(username, api_key):
    """Fetch all videos using pagination"""

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "tiktok-scraper7.p.rapidapi.com"
    }

    base_url = "https://tiktok-scraper7.p.rapidapi.com/user/posts"

    all_videos = []
    cursor = None
    page = 1

    while True:
        params = {
            "unique_id": username,
            "count": 35
        }

        if cursor:
            params['cursor'] = cursor

        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get('code') != 0:
                break

            video_list = data.get('data', {}).get('videos', [])
            all_videos.extend(video_list)

            has_more = data.get('data', {}).get('hasMore', False)
            cursor = data.get('data', {}).get('cursor')

            if not has_more or not cursor:
                break

            page += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"  Error on page {page}: {e}")
            break

    return all_videos


def parse_video_data(item):
    """Parse video data from API response"""
    try:
        video_id = item.get('video_id') or item.get('aweme_id')
        if not video_id:
            return None

        author = item.get('author', {})
        author_username = author.get('unique_id', '') or author.get('uniqueId', '')

        views = int(item.get('play_count', 0))
        likes = int(item.get('digg_count', 0))
        comments = int(item.get('comment_count', 0))
        shares = int(item.get('share_count', 0))
        bookmarks = int(item.get('collect_count', 0))

        thumbnail_url = item.get('cover') or item.get('origin_cover')
        music_info = item.get('music_info', {})
        music_title = item.get('music') or music_info.get('title', '')
        title = item.get('title', '')
        hashtags = re.findall(r'#(\w+)', title)

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
        return None


def scrape_account(username, api_key, db):
    """Scrape a single account"""

    print(f"\n{'='*70}")
    print(f"Scraping @{username}")
    print(f"{'='*70}")

    current_count = db.query(Video).filter(Video.author_username == username).count()
    print(f"Current videos in SQLite: {current_count}")

    raw_videos = fetch_all_videos_with_pagination(username, api_key)

    if not raw_videos:
        print(f"❌ No videos fetched for @{username}")
        return

    videos = []
    for raw_video in raw_videos:
        parsed = parse_video_data(raw_video)
        if parsed:
            videos.append(parsed)

    print(f"✓ Fetched {len(videos)} videos from API")

    new_count = 0
    updated_count = 0

    for video_data in videos:
        video_id = video_data['id']

        existing = db.query(Video).filter(Video.id == video_id).first()

        if existing:
            existing.views = video_data['views']
            existing.likes = video_data['likes']
            existing.comments = video_data['comments']
            existing.shares = video_data['shares']
            existing.bookmarks = video_data.get('bookmarks', 0)
            existing.scraped_at = datetime.utcnow()
            updated_count += 1
        else:
            video = Video(**video_data)
            db.add(video)
            new_count += 1

    db.commit()

    print(f"✅ Complete: {new_count} new, {updated_count} updated")

    final_count = db.query(Video).filter(Video.author_username == username).count()
    print(f"📊 Total in SQLite: {final_count} videos")


def main():
    """Main scraping function"""

    accounts = [
        "karissa.curious",
        "max.curious1",
        "mari.curious"
    ]

    api_key = os.environ['RAPIDAPI_KEY']
    db = SessionLocal()

    try:
        print(f"\n{'#'*70}")
        print(f"# Scraping All Accounts to SQLite")
        print(f"{'#'*70}")

        for username in accounts:
            scrape_account(username, api_key, db)
            time.sleep(2)

        print(f"\n{'#'*70}")
        print(f"# ALL ACCOUNTS SCRAPED!")
        print(f"{'#'*70}\n")

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
