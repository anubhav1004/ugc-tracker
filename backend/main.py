from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import asyncio
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# Load environment variables
load_dotenv()

from database import get_db, init_db, Video, VideoHistory, TrendingAudio, Hashtag, SearchHistory, ScrapingJob, Collection, Account, VideoCollection, AccountCollection
from scrapers.tiktok_scraper import TikTokScraper
from scrapers.youtube_scraper import YouTubeScraper
from scrapers.trending_audio_scraper import TrendingAudioScraper
from scrapers.url_scraper import URLScraper

app = FastAPI(title="Social Media Tracker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = BackgroundScheduler()

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    platform: str = "tiktok"  # tiktok, youtube, instagram
    limit: int = 50
    country: Optional[str] = None


class VideoResponse(BaseModel):
    id: str
    platform: str
    url: str
    thumbnail: Optional[str]
    caption: Optional[str]
    author_username: Optional[str]
    author_nickname: Optional[str]
    author_avatar: Optional[str]
    views: int
    likes: int
    comments: int
    shares: int
    music_id: Optional[str]
    music_title: Optional[str]
    music_author: Optional[str]
    hashtags: Optional[List[str]]
    posted_at: Optional[datetime]

    class Config:
        from_attributes = True


class TrendingAudioResponse(BaseModel):
    id: int
    music_id: str
    title: str
    author: Optional[str]
    play_url: Optional[str]
    thumbnail: Optional[str]
    total_videos: int
    rank: Optional[int]
    country: Optional[str]
    trending_date: datetime

    class Config:
        from_attributes = True


class URLScrapeRequest(BaseModel):
    urls: List[str]  # List of video URLs to scrape


class URLScrapeResponse(BaseModel):
    id: str
    platform: str
    url: str
    thumbnail: Optional[str]
    caption: Optional[str]
    author_username: Optional[str]
    author_nickname: Optional[str]
    author_avatar: Optional[str]
    views: int
    likes: int
    comments: int
    shares: int
    bookmarks: Optional[int] = 0
    music_title: Optional[str]
    music_author: Optional[str]
    hashtags: Optional[List[str]]
    duration: Optional[int]
    posted_at: Optional[datetime]
    scraped_at: datetime


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database initialized")


# Health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "Social Media Tracker API is running"}


# Search endpoints
@app.post("/api/search/hashtag", response_model=List[VideoResponse])
async def search_hashtag(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Search for videos by hashtag"""

    # Create scraping job
    job = ScrapingJob(
        job_type="hashtag_search",
        platform=request.platform,
        query=request.query,
        country=request.country,
        status="running",
        started_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()

    try:
        videos_data = []

        if request.platform == "tiktok":
            async with TikTokScraper() as scraper:
                videos_data = await scraper.search_hashtag(request.query, request.limit)

        elif request.platform == "youtube":
            scraper = YouTubeScraper()
            videos_data = await scraper.search_hashtag(request.query, request.limit)

        else:
            job.status = "failed"
            job.error_message = f"Platform {request.platform} not supported"
            db.commit()
            raise HTTPException(status_code=400, detail=f"Platform {request.platform} not supported")

        # Save videos to database
        video_models = []
        for video_data in videos_data:
            # Check if video already exists
            existing = db.query(Video).filter(
                Video.id == video_data['id'],
                Video.platform == video_data['platform']
            ).first()

            if existing:
                # Update existing video
                for key, value in video_data.items():
                    setattr(existing, key, value)
                video_models.append(existing)
            else:
                # Create new video
                video = Video(**video_data)
                db.add(video)
                video_models.append(video)

        db.commit()

        # Update job status
        job.status = "completed"
        job.progress = len(videos_data)
        job.total = request.limit
        job.completed_at = datetime.utcnow()
        db.commit()

        # Log search history
        search_history = SearchHistory(
            query=request.query,
            query_type="hashtag",
            platform=request.platform,
            country=request.country,
            results_count=len(videos_data)
        )
        db.add(search_history)
        db.commit()

        return video_models

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search/term", response_model=List[VideoResponse])
async def search_term(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Search for videos by search term"""

    try:
        videos_data = []

        if request.platform == "tiktok":
            async with TikTokScraper() as scraper:
                videos_data = await scraper.search_term(request.query, request.limit)

        elif request.platform == "youtube":
            scraper = YouTubeScraper()
            videos_data = await scraper.search_term(request.query, request.limit)

        else:
            raise HTTPException(status_code=400, detail=f"Platform {request.platform} not supported")

        # Save videos to database
        video_models = []
        for video_data in videos_data:
            existing = db.query(Video).filter(
                Video.id == video_data['id'],
                Video.platform == video_data['platform']
            ).first()

            if existing:
                for key, value in video_data.items():
                    setattr(existing, key, value)
                video_models.append(existing)
            else:
                video = Video(**video_data)
                db.add(video)
                video_models.append(video)

        db.commit()

        # Log search history
        search_history = SearchHistory(
            query=request.query,
            query_type="term",
            platform=request.platform,
            country=request.country,
            results_count=len(videos_data)
        )
        db.add(search_history)
        db.commit()

        return video_models

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trending/audio", response_model=List[TrendingAudioResponse])
async def get_trending_audio(
    country: str = Query("US", description="Country code (e.g., US, UK, IN)"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get trending audio/music by country"""

    try:
        # Check if we have recent cached data (less than 1 hour old)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        cached_audio = db.query(TrendingAudio).filter(
            TrendingAudio.country == country,
            TrendingAudio.trending_date >= one_hour_ago
        ).order_by(TrendingAudio.rank).limit(limit).all()

        if cached_audio and len(cached_audio) >= limit:
            return cached_audio

        # Scrape fresh data
        scraper = TrendingAudioScraper(country=country)
        trending_data = await scraper.get_trending_audio(limit=limit)

        # Save to database
        audio_models = []
        for audio_data in trending_data:
            audio = TrendingAudio(**audio_data)
            db.add(audio)
            audio_models.append(audio)

        db.commit()

        return audio_models

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/videos")
async def get_videos(
    platform: Optional[str] = None,
    creator: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    is_spark_ad: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get videos from database with optional filtering"""

    query = db.query(Video)

    # Apply filters
    if platform:
        query = query.filter(Video.platform == platform)
    if creator:
        query = query.filter(Video.author_username == creator)
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from)
            query = query.filter(Video.posted_at >= date_from_obj)
        except ValueError:
            pass  # Ignore invalid date format
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to)
            query = query.filter(Video.posted_at <= date_to_obj)
        except ValueError:
            pass  # Ignore invalid date format
    if is_spark_ad is not None:
        query = query.filter(Video.is_spark_ad == is_spark_ad)

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    videos = query.order_by(Video.scraped_at.desc()).offset(offset).limit(limit).all()

    # Return with pagination metadata
    return {
        "videos": videos,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }


@app.get("/api/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, db: Session = Depends(get_db)):
    """Get a specific video by ID"""

    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return video


@app.patch("/api/videos/{video_id}/spark-ad")
async def update_spark_ad_status(
    video_id: str,
    is_spark_ad: bool = Query(..., description="Mark video as Spark Ad or organic"),
    db: Session = Depends(get_db)
):
    """Update the Spark Ads status of a video"""

    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video.is_spark_ad = is_spark_ad
    db.commit()
    db.refresh(video)

    return {
        "success": True,
        "video_id": video_id,
        "is_spark_ad": is_spark_ad,
        "message": f"Video marked as {'Spark Ad' if is_spark_ad else 'organic'}"
    }


@app.get("/api/creators")
async def get_creators(
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of unique creators/authors from videos (only from active accounts)"""

    from sqlalchemy import func

    # Join with Account table to filter by is_active
    query = db.query(
        Video.author_username,
        func.max(Video.author_nickname).label('author_nickname')
    ).join(
        Account,
        (Video.author_username == Account.username) & (Video.platform == Account.platform)
    ).filter(
        Account.is_active == True  # Only show creators from active accounts
    ).group_by(Video.author_username)

    if platform:
        query = query.filter(Video.platform == platform)

    creators = query.filter(Video.author_username.isnot(None)).all()

    return [
        {
            "username": creator.author_username,
            "nickname": creator.author_nickname or creator.author_username
        }
        for creator in creators
    ]


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""

    total_videos = db.query(Video).count()
    total_tiktok = db.query(Video).filter(Video.platform == "tiktok").count()
    total_youtube = db.query(Video).filter(Video.platform == "youtube").count()
    total_trending_audio = db.query(TrendingAudio).count()
    total_hashtags = db.query(Hashtag).count()

    return {
        "total_videos": total_videos,
        "videos_by_platform": {
            "tiktok": total_tiktok,
            "youtube": total_youtube,
        },
        "trending_audio_count": total_trending_audio,
        "hashtags_tracked": total_hashtags,
    }


@app.get("/api/analytics/timeseries")
async def get_analytics_timeseries(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get time series data for views, installs, and trials"""
    from sqlalchemy import func
    from datetime import date

    # Get date range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)

    # Query videos within date range
    videos = db.query(Video).filter(
        Video.posted_at >= datetime.combine(start_date, datetime.min.time())
    ).all()

    # Group by date
    data_by_date = {}
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        data_by_date[current_date] = {
            'views': 0,
            'installs': 0,
            'trial_started': 0
        }

    # Aggregate data
    for video in videos:
        video_date = (video.posted_at or video.scraped_at).date()
        if video_date in data_by_date:
            data_by_date[video_date]['views'] += video.views or 0
            data_by_date[video_date]['installs'] += video.installs or 0
            data_by_date[video_date]['trial_started'] += video.trial_started or 0

    # Format response
    result = []
    for date_key in sorted(data_by_date.keys()):
        result.append({
            'date': date_key.strftime('%Y-%m-%d'),
            'views': data_by_date[date_key]['views'],
            'installs': data_by_date[date_key]['installs'],
            'trial_started': data_by_date[date_key]['trial_started']
        })

    return result


@app.get("/api/trending/videos", response_model=List[VideoResponse])
async def get_trending_videos(
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get trending TikTok videos"""

    try:
        # Check for cached trending videos (less than 30 minutes old)
        thirty_min_ago = datetime.utcnow() - timedelta(minutes=30)
        cached_videos = db.query(Video).filter(
            Video.platform == "tiktok",
            Video.scraped_at >= thirty_min_ago
        ).order_by(Video.views.desc()).limit(limit).all()

        if cached_videos and len(cached_videos) >= limit:
            return cached_videos

        # Scrape fresh trending videos
        async with TikTokScraper() as scraper:
            videos_data = await scraper.get_trending_videos(limit=limit)

        # Save to database
        video_models = []
        for video_data in videos_data:
            existing = db.query(Video).filter(
                Video.id == video_data['id'],
                Video.platform == video_data['platform']
            ).first()

            if existing:
                for key, value in video_data.items():
                    setattr(existing, key, value)
                video_models.append(existing)
            else:
                video = Video(**video_data)
                db.add(video)
                video_models.append(video)

        db.commit()

        return video_models

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_or_update_account(db: Session, video: Video):
    """Create or update account from video data"""
    if not video.author_username:
        return None

    # Check if account exists
    account = db.query(Account).filter(
        Account.username == video.author_username,
        Account.platform == video.platform
    ).first()

    if account:
        # Update last_scraped and reactivate if deleted
        account.last_scraped = datetime.utcnow()
        account.avatar = video.author_avatar or account.avatar
        account.nickname = video.author_nickname or account.nickname
        account.is_active = True  # Reactivate account if it was deleted
    else:
        # Create new account
        account = Account(
            username=video.author_username,
            platform=video.platform,
            nickname=video.author_nickname,
            avatar=video.author_avatar,
            profile_url=f"https://www.tiktok.com/@{video.author_username}" if video.platform == 'tiktok' else None,
            total_videos=0,
            total_views=0,
            total_likes=0,
            total_followers=0,
            is_active=True
        )
        db.add(account)

    db.commit()
    db.refresh(account)

    # Refresh account stats
    videos = db.query(Video).filter(
        Video.author_username == account.username,
        Video.platform == account.platform
    ).all()

    account.total_videos = len(videos)
    account.total_views = sum(v.views for v in videos)
    account.total_likes = sum(v.likes for v in videos)
    db.commit()

    return account


def save_video_snapshot(db: Session, video: Video):
    """Save a daily snapshot of video metrics for growth tracking"""
    from datetime import date as date_type

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Check if snapshot already exists for today
    existing_snapshot = db.query(VideoHistory).filter(
        VideoHistory.video_id == video.id,
        VideoHistory.platform == video.platform,
        VideoHistory.snapshot_date >= today
    ).first()

    if existing_snapshot:
        # Update existing snapshot with latest data
        existing_snapshot.views = video.views
        existing_snapshot.likes = video.likes
        existing_snapshot.comments = video.comments
        existing_snapshot.shares = video.shares
        existing_snapshot.saves = video.bookmarks or 0
    else:
        # Get yesterday's snapshot to calculate growth
        yesterday = today - timedelta(days=1)
        previous_snapshot = db.query(VideoHistory).filter(
            VideoHistory.video_id == video.id,
            VideoHistory.platform == video.platform,
            VideoHistory.snapshot_date >= yesterday,
            VideoHistory.snapshot_date < today
        ).first()

        # Calculate growth
        views_growth = 0
        likes_growth = 0
        comments_growth = 0

        if previous_snapshot:
            views_growth = video.views - previous_snapshot.views
            likes_growth = video.likes - previous_snapshot.likes
            comments_growth = video.comments - previous_snapshot.comments

        # Create new snapshot
        snapshot = VideoHistory(
            video_id=video.id,
            platform=video.platform,
            views=video.views,
            likes=video.likes,
            comments=video.comments,
            shares=video.shares,
            saves=video.bookmarks or 0,
            views_growth=max(0, views_growth),  # Ensure non-negative
            likes_growth=max(0, likes_growth),
            comments_growth=max(0, comments_growth),
            snapshot_date=today
        )
        db.add(snapshot)

    db.commit()


def normalize_url_or_username(input_str: str) -> str:
    """
    Convert username to full URL or return URL as-is
    Supports formats:
    - Full URL: https://www.tiktok.com/@username -> returns as-is
    - Username with @: @username -> https://www.tiktok.com/@username
    - Username without @: username -> https://www.tiktok.com/@username
    - Instagram: instagram:username -> https://www.instagram.com/username/
    """
    input_str = input_str.strip()

    # If it's already a URL, return as-is
    if input_str.startswith('http://') or input_str.startswith('https://'):
        return input_str

    # If it contains domain names, assume it's a URL without protocol
    if 'tiktok.com' in input_str or 'instagram.com' in input_str or 'youtube.com' in input_str:
        if not input_str.startswith('http'):
            return f'https://{input_str}'
        return input_str

    # Check for platform prefix (instagram:username or ig:username)
    if input_str.startswith('instagram:') or input_str.startswith('ig:'):
        username = input_str.split(':', 1)[1].strip().lstrip('@')
        return f'https://www.instagram.com/{username}/'

    # Check for platform prefix (tiktok:username or tt:username)
    if input_str.startswith('tiktok:') or input_str.startswith('tt:'):
        username = input_str.split(':', 1)[1].strip().lstrip('@')
        return f'https://www.tiktok.com/@{username}'

    # Default: assume it's a TikTok username
    username = input_str.lstrip('@')
    return f'https://www.tiktok.com/@{username}'


async def background_scrape_task(normalized_urls: List[str]):
    """Background task for scraping URLs"""
    from database import SessionLocal
    db = SessionLocal()

    try:
        results = []
        errors = []

        # Get or create default collection
        default_collection = db.query(Collection).filter(Collection.is_default == True).first()
        if not default_collection:
            default_collection = Collection(name="Default", is_default=True, description="All tracked videos")
            db.add(default_collection)
            db.commit()
            db.refresh(default_collection)

        # URLScraper will automatically use RAPIDAPI_KEY_INSTAGRAM and RAPIDAPI_KEY_TIKTOK
        async with URLScraper(rapidapi_key=None) as scraper:
            for url in normalized_urls:
                try:
                    # Detect if this is a profile or video URL
                    url_type = scraper.detect_url_type(url)

                    if url_type == 'profile':
                        # Scrape all videos from profile
                        profile_data = await scraper.scrape_profile(url, limit=100)

                        # Save all videos from profile to database (batched for performance)
                        for video_data in profile_data['videos']:
                            # Remove internal fields that aren't part of the Video model
                            video_data.pop('_is_video', None)

                            existing = db.query(Video).filter(
                                Video.id == video_data['id'],
                                Video.platform == video_data['platform']
                            ).first()

                            if existing:
                                # Update existing
                                for key, value in video_data.items():
                                    setattr(existing, key, value)
                                results.append(existing)
                            else:
                                # Create new
                                video = Video(**video_data)
                                db.add(video)
                                results.append(video)

                        # Batch commit all video updates/inserts
                        db.commit()

                        # Process post-video operations
                        for video in results:
                            # Save daily snapshot for growth tracking
                            save_video_snapshot(db, video)

                            # Create or update account
                            account = create_or_update_account(db, video)

                            # Add to default collection if not already there
                            existing_vc = db.query(VideoCollection).filter(
                                VideoCollection.video_id == video.id,
                                VideoCollection.collection_id == default_collection.id
                            ).first()

                            if not existing_vc:
                                vc = VideoCollection(video_id=video.id, collection_id=default_collection.id)
                                db.add(vc)

                        # Final commit for snapshots and collections
                        db.commit()

                    elif url_type == 'video':
                        # Scrape single video
                        video_data = await scraper.scrape_url(url)

                        # Remove internal fields that aren't part of the Video model
                        video_data.pop('_is_video', None)

                        # Save to database
                        existing = db.query(Video).filter(
                            Video.id == video_data['id'],
                            Video.platform == video_data['platform']
                        ).first()

                        if existing:
                            # Update existing
                            for key, value in video_data.items():
                                setattr(existing, key, value)
                            db.commit()
                            results.append(existing)
                        else:
                            # Create new
                            video = Video(**video_data)
                            db.add(video)
                            db.commit()
                            results.append(video)

                        # Create or update account
                        account = create_or_update_account(db, results[-1])

                        # Add to default collection if not already there
                        existing_vc = db.query(VideoCollection).filter(
                            VideoCollection.video_id == results[-1].id,
                            VideoCollection.collection_id == default_collection.id
                        ).first()

                        if not existing_vc:
                            vc = VideoCollection(video_id=results[-1].id, collection_id=default_collection.id)
                            db.add(vc)
                            db.commit()
                    else:
                        raise ValueError(f"Could not determine URL type for: {url}")

                except Exception as e:
                    import traceback
                    error_details = {
                        "url": url,
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
                    print(f"ERROR scraping {url}: {str(e)}")
                    print(f"Traceback: {traceback.format_exc()}")
                    errors.append(error_details)

        print(f"Background scraping completed. Results: {len(results)}, Errors: {len(errors)}")

    except Exception as e:
        print(f"Background scraping error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


@app.post("/api/scrape/urls")
async def scrape_urls(
    request: URLScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Scrape video metrics from URLs or usernames (background processing)
    Supports:
    - Full URLs: https://www.tiktok.com/@username
    - Usernames: username or @username (defaults to TikTok)
    - Platform prefix: instagram:username or tiktok:username

    Returns immediately and processes scraping in background.
    """

    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

    # Normalize all inputs to full URLs
    normalized_urls = [normalize_url_or_username(url) for url in request.urls]

    # Add background task
    background_tasks.add_task(background_scrape_task, normalized_urls)

    # Return immediately
    return {
        "message": "Scraping started in background",
        "urls": normalized_urls,
        "status": "processing"
    }


def apply_collection_filter(query, collection_id: int, db: Session):
    """Helper function to filter videos by collection"""
    if not collection_id:
        return query

    # Get account IDs in the collection
    account_ids = db.query(AccountCollection.account_id).filter(
        AccountCollection.collection_id == collection_id
    ).all()
    account_ids_list = [aid[0] for aid in account_ids]

    # Get accounts
    accounts = db.query(Account).filter(Account.id.in_(account_ids_list)).all()
    account_usernames = [acc.username for acc in accounts]

    # Filter videos by author username
    if account_usernames:
        query = query.filter(Video.author_username.in_(account_usernames))
    else:
        # No accounts in collection, return empty result
        query = query.filter(Video.id == None)

    return query


@app.get("/api/analytics/overview")
async def get_analytics_overview(
    days: int = Query(7, ge=1, le=365),
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    collection_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """Get analytics overview for metrics cards - shows ALL videos' current stats"""

    # Don't filter by date for overview - show all videos' current cumulative stats
    # The date filter only affects the historical growth chart
    query = db.query(Video)

    # Apply collection filter
    query = apply_collection_filter(query, collection_id, db)

    # Apply platform filter
    if platform:
        platforms = [p.strip().lower() for p in platform.split(',')]
        query = query.filter(Video.platform.in_(platforms))

    # Apply metric type filter
    if metric_type == "organic":
        query = query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        query = query.filter(Video.is_spark_ad == True)
    # metric_type == "total" means no filter

    # Use SQL aggregations instead of loading all videos into memory
    # This is much faster and reduces memory usage
    aggregates = query.with_entities(
        func.sum(Video.views).label('total_views'),
        func.sum(Video.likes).label('total_likes'),
        func.sum(Video.comments).label('total_comments'),
        func.sum(Video.shares).label('total_shares'),
        func.sum(func.coalesce(Video.bookmarks, 0)).label('total_bookmarks')
    ).first()

    if not aggregates or aggregates.total_views is None:
        return {
            "views": {"total": 0, "change": 0},
            "engagement": {"total": 0, "change": 0},
            "likes": {"total": 0, "change": 0},
            "comments": {"total": 0, "change": 0},
            "shares": {"total": 0, "change": 0},
            "saves": {"total": 0, "change": 0}
        }

    # Calculate totals from SQL aggregation results
    total_views = aggregates.total_views or 0
    total_likes = aggregates.total_likes or 0
    total_comments = aggregates.total_comments or 0
    total_shares = aggregates.total_shares or 0
    total_bookmarks = aggregates.total_bookmarks or 0
    total_engagement = total_likes + total_comments + total_shares + total_bookmarks

    return {
        "views": {"total": total_views, "change": 0},
        "engagement": {"total": total_engagement, "change": 0},
        "likes": {"total": total_likes, "change": 0},
        "comments": {"total": total_comments, "change": 0},
        "shares": {"total": total_shares, "change": 0},
        "saves": {"total": total_bookmarks, "change": 0}
    }


@app.get("/api/analytics/views-over-time")
async def get_views_over_time(
    days: int = Query(7, ge=1, le=365),
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    collection_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """Get cumulative views over time based on video posted dates"""

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get videos with posted_at dates within the specified range
    query = db.query(Video).filter(
        Video.posted_at.isnot(None),
        Video.posted_at >= start_date,
        Video.posted_at <= end_date
    )

    # Apply collection filter
    query = apply_collection_filter(query, collection_id, db)

    # Apply platform filter
    if platform:
        platforms = [p.strip().lower() for p in platform.split(',')]
        query = query.filter(Video.platform.in_(platforms))

    # Apply metric type filter
    if metric_type == "organic":
        query = query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        query = query.filter(Video.is_spark_ad == True)

    videos = query.order_by(Video.posted_at).all()

    if not videos:
        return []

    # Use the query date range instead of finding from data
    earliest_date = start_date
    latest_date = end_date

    # Generate all dates in the range
    from datetime import date as date_type
    current_date = earliest_date.date()
    end_date = latest_date.date()

    cumulative_data = []
    cumulative_views = 0
    videos_by_date = {}

    # Group videos by posted date
    for video in videos:
        if video.posted_at:
            date_key = video.posted_at.date()
            if date_key not in videos_by_date:
                videos_by_date[date_key] = []
            videos_by_date[date_key].append(video)

    # Calculate cumulative views for each date
    while current_date <= end_date:
        # Add views from videos posted on this date
        if current_date in videos_by_date:
            for video in videos_by_date[current_date]:
                cumulative_views += video.views

        cumulative_data.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "views": cumulative_views
        })

        current_date += timedelta(days=1)

    return cumulative_data


@app.get("/api/analytics/historical-growth")
async def get_historical_growth(
    days: int = Query(30, ge=1, le=365),
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    collection_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get true daily growth data from historical snapshots.
    Returns actual day-by-day view growth, not cumulative totals.
    """

    # Calculate date range
    end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days)

    # Get video IDs to track based on filters
    video_query = db.query(Video.id)

    # Apply collection filter
    if collection_id:
        video_ids_in_collection = db.query(VideoCollection.video_id).filter(
            VideoCollection.collection_id == collection_id
        ).all()
        video_ids = [v[0] for v in video_ids_in_collection]
        video_query = video_query.filter(Video.id.in_(video_ids))

    # Apply platform filter
    if platform:
        platforms = [p.strip().lower() for p in platform.split(',')]
        video_query = video_query.filter(Video.platform.in_(platforms))

    # Apply metric type filter
    if metric_type == "organic":
        video_query = video_query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        video_query = video_query.filter(Video.is_spark_ad == True)

    tracked_video_ids = [v[0] for v in video_query.all()]

    if not tracked_video_ids:
        return []

    # Query historical snapshots
    snapshots = db.query(VideoHistory).filter(
        VideoHistory.video_id.in_(tracked_video_ids),
        VideoHistory.snapshot_date >= start_date,
        VideoHistory.snapshot_date <= end_date
    ).order_by(VideoHistory.snapshot_date).all()

    if not snapshots:
        return []

    # Group snapshots by date and aggregate
    from collections import defaultdict
    daily_data = defaultdict(lambda: {
        'views': 0,
        'views_growth': 0,
        'likes': 0,
        'likes_growth': 0,
        'comments': 0,
        'comments_growth': 0,
        'shares': 0,
        'saves': 0
    })

    for snapshot in snapshots:
        date_key = snapshot.snapshot_date.date()
        daily_data[date_key]['views'] += snapshot.views
        daily_data[date_key]['views_growth'] += snapshot.views_growth
        daily_data[date_key]['likes'] += snapshot.likes
        daily_data[date_key]['likes_growth'] += snapshot.likes_growth
        daily_data[date_key]['comments'] += snapshot.comments
        daily_data[date_key]['comments_growth'] += snapshot.comments_growth
        daily_data[date_key]['shares'] += snapshot.shares
        daily_data[date_key]['saves'] += snapshot.saves

    # Generate complete date range
    result = []
    current_date = start_date.date()
    end_date_only = end_date.date()

    while current_date <= end_date_only:
        data = daily_data.get(current_date, {
            'views': 0,
            'views_growth': 0,
            'likes': 0,
            'likes_growth': 0,
            'comments': 0,
            'comments_growth': 0,
            'shares': 0,
            'saves': 0
        })

        result.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'views': data['views'],
            'views_growth': data['views_growth'],
            'likes': data['likes'],
            'likes_growth': data['likes_growth'],
            'comments': data['comments'],
            'comments_growth': data['comments_growth'],
            'shares': data['shares'],
            'saves': data['saves'],
            'engagement': data['likes'] + data['comments'] + data['shares'] + data['saves']
        })

        current_date += timedelta(days=1)

    return result


@app.get("/api/analytics/historical-growth-split")
async def get_historical_growth_split(
    days: int = Query(30, ge=1, le=365),
    platform: str = Query(None),
    collection_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get historical growth data split by organic vs spark ads.
    Returns two separate datasets for comparison.
    """

    # Calculate date range
    end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days)

    # Helper function to get data for a specific type
    def get_data_for_type(is_spark_ad_filter):
        video_query = db.query(Video.id)

        # Apply collection filter
        if collection_id:
            video_ids_in_collection = db.query(VideoCollection.video_id).filter(
                VideoCollection.collection_id == collection_id
            ).all()
            video_ids = [v[0] for v in video_ids_in_collection]
            video_query = video_query.filter(Video.id.in_(video_ids))

        # Apply platform filter
        if platform:
            platforms = [p.strip().lower() for p in platform.split(',')]
            video_query = video_query.filter(Video.platform.in_(platforms))

        # Apply spark ad filter
        video_query = video_query.filter(Video.is_spark_ad == is_spark_ad_filter)

        tracked_video_ids = [v[0] for v in video_query.all()]

        if not tracked_video_ids:
            return []

        # Query historical snapshots
        snapshots = db.query(VideoHistory).filter(
            VideoHistory.video_id.in_(tracked_video_ids),
            VideoHistory.snapshot_date >= start_date,
            VideoHistory.snapshot_date <= end_date
        ).order_by(VideoHistory.snapshot_date).all()

        if not snapshots:
            return []

        # Group snapshots by date
        from collections import defaultdict
        daily_data = defaultdict(lambda: {'views_growth': 0})

        for snapshot in snapshots:
            date_key = snapshot.snapshot_date.date()
            daily_data[date_key]['views_growth'] += snapshot.views_growth

        # Generate complete date range
        result = []
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            views_growth = daily_data.get(current_date, {}).get('views_growth', 0)
            result.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'views_growth': views_growth
            })
            current_date += timedelta(days=1)

        return result

    # Get organic and spark ad data separately
    organic_data = get_data_for_type(False)
    spark_ad_data = get_data_for_type(True)

    return {
        'organic': organic_data,
        'spark_ads': spark_ad_data
    }


@app.get("/api/analytics/most-viral")
async def get_most_viral_videos(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1, le=365),
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    collection_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """Get most viral videos based on engagement rate"""

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Query videos in date range
    query = db.query(Video).filter(
        Video.posted_at.isnot(None),
        Video.posted_at >= start_date,
        Video.posted_at <= end_date
    )

    # Apply collection filter
    query = apply_collection_filter(query, collection_id, db)

    # Apply platform filter
    if platform:
        platforms = [p.strip().lower() for p in platform.split(',')]
        query = query.filter(Video.platform.in_(platforms))

    # Apply metric type filter
    if metric_type == "organic":
        query = query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        query = query.filter(Video.is_spark_ad == True)

    videos = query.order_by(Video.views.desc()).limit(limit * 2).all()

    # Calculate engagement rate and sort
    video_stats = []
    for video in videos:
        if video.views > 0:
            engagement_rate = ((video.likes + video.comments + video.shares) / video.views) * 100
            video_stats.append({
                "id": video.id,
                "platform": video.platform,
                "url": video.url,
                "thumbnail": video.thumbnail,
                "caption": video.caption,
                "author_username": video.author_username,
                "author_nickname": video.author_nickname,
                "author_avatar": video.author_avatar,
                "views": video.views,
                "likes": video.likes,
                "comments": video.comments,
                "shares": video.shares,
                "bookmarks": video.bookmarks,
                "engagement": video.likes + video.comments + video.shares,
                "engagement_rate": round(engagement_rate, 2),
                "posted_at": video.posted_at,
                "scraped_at": video.scraped_at
            })

    # Sort by engagement rate
    video_stats.sort(key=lambda x: x['engagement_rate'], reverse=True)

    return video_stats[:limit]


@app.get("/api/analytics/virality-analysis")
async def get_virality_analysis(
    days: int = Query(7, ge=1, le=365),
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    collection_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """Get virality median analysis data"""

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Query videos in date range
    query = db.query(Video).filter(
        Video.posted_at.isnot(None),
        Video.posted_at >= start_date,
        Video.posted_at <= end_date
    )

    # Apply collection filter
    query = apply_collection_filter(query, collection_id, db)

    # Apply platform filter
    if platform:
        platforms = [p.strip().lower() for p in platform.split(',')]
        query = query.filter(Video.platform.in_(platforms))

    # Apply metric type filter
    if metric_type == "organic":
        query = query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        query = query.filter(Video.is_spark_ad == True)

    videos = query.all()

    if not videos:
        return {
            "below_1x": 0,
            "1x_to_5x": 0,
            "5x_to_10x": 0,
            "10x_to_25x": 0,
            "25x_to_50x": 0,
            "50x_to_100x": 0,
            "above_100x": 0
        }

    # Calculate median views
    view_counts = sorted([v.views for v in videos])
    median_views = view_counts[len(view_counts) // 2]

    # Categorize videos by virality multiplier
    categories = {
        "below_1x": 0,
        "1x_to_5x": 0,
        "5x_to_10x": 0,
        "10x_to_25x": 0,
        "25x_to_50x": 0,
        "50x_to_100x": 0,
        "above_100x": 0
    }

    for video in videos:
        if median_views == 0:
            continue

        multiplier = video.views / median_views

        if multiplier < 1:
            categories["below_1x"] += 1
        elif multiplier < 5:
            categories["1x_to_5x"] += 1
        elif multiplier < 10:
            categories["5x_to_10x"] += 1
        elif multiplier < 25:
            categories["10x_to_25x"] += 1
        elif multiplier < 50:
            categories["25x_to_50x"] += 1
        elif multiplier < 100:
            categories["50x_to_100x"] += 1
        else:
            categories["above_100x"] += 1

    return categories


@app.get("/api/analytics/duration-analysis")
async def get_duration_analysis(
    days: int = Query(7, ge=1, le=365),
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    collection_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """Get duration analysis data"""

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Query videos in date range with duration
    query = db.query(Video).filter(
        Video.duration != None,
        Video.posted_at.isnot(None),
        Video.posted_at >= start_date,
        Video.posted_at <= end_date
    )

    # Apply collection filter
    query = apply_collection_filter(query, collection_id, db)

    # Apply platform filter
    if platform:
        platforms = [p.strip().lower() for p in platform.split(',')]
        query = query.filter(Video.platform.in_(platforms))

    # Apply metric type filter
    if metric_type == "organic":
        query = query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        query = query.filter(Video.is_spark_ad == True)

    videos = query.all()

    if not videos:
        return []

    # Group by duration ranges
    duration_groups = {
        "0-5": [],
        "5-10": [],
        "10-20": [],
        "20-30": [],
        "30-45": [],
        "45-60": [],
        "60+": []
    }

    for video in videos:
        duration = video.duration
        if duration < 5:
            duration_groups["0-5"].append(video.views)
        elif duration < 10:
            duration_groups["5-10"].append(video.views)
        elif duration < 20:
            duration_groups["10-20"].append(video.views)
        elif duration < 30:
            duration_groups["20-30"].append(video.views)
        elif duration < 45:
            duration_groups["30-45"].append(video.views)
        elif duration < 60:
            duration_groups["45-60"].append(video.views)
        else:
            duration_groups["60+"].append(video.views)

    # Calculate average views per duration range
    result = []
    for range_name, views_list in duration_groups.items():
        if views_list:
            avg_views = sum(views_list) / len(views_list)
            result.append({
                "range": range_name,
                "average_views": int(avg_views),
                "video_count": len(views_list)
            })

    return result


@app.get("/api/analytics/metrics-breakdown")
async def get_metrics_breakdown(
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get daily and weekly metrics breakdown"""

    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=1)
    seven_days_ago = now - timedelta(days=7)

    # Daily videos query - filter by posted_at instead of scraped_at
    daily_query = db.query(Video).filter(
        Video.posted_at.isnot(None),
        Video.posted_at >= one_day_ago
    )
    if platform:
        platforms = [p.strip().upper() for p in platform.split(',')]
        daily_query = daily_query.filter(Video.platform.in_(platforms))
    if metric_type == "organic":
        daily_query = daily_query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        daily_query = daily_query.filter(Video.is_spark_ad == True)
    daily_videos = daily_query.all()

    # Weekly videos query - filter by posted_at instead of scraped_at
    weekly_query = db.query(Video).filter(
        Video.posted_at.isnot(None),
        Video.posted_at >= seven_days_ago
    )
    if platform:
        platforms = [p.strip().upper() for p in platform.split(',')]
        weekly_query = weekly_query.filter(Video.platform.in_(platforms))
    if metric_type == "organic":
        weekly_query = weekly_query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        weekly_query = weekly_query.filter(Video.is_spark_ad == True)
    weekly_videos = weekly_query.all()

    def calculate_averages(videos):
        if not videos:
            return {
                "avg_views": 0,
                "avg_views_gain": 0,
                "avg_comments_gain": 0,
                "avg_likes_gain": 0
            }

        total_views = sum(v.views for v in videos)
        total_likes = sum(v.likes for v in videos)
        total_comments = sum(v.comments for v in videos)

        return {
            "avg_views": int(total_views / len(videos)),
            "avg_views_gain": int(total_views / len(videos)),
            "avg_comments_gain": int(total_comments / len(videos)),
            "avg_likes_gain": int(total_likes / len(videos))
        }

    return {
        "daily": calculate_averages(daily_videos),
        "weekly": calculate_averages(weekly_videos)
    }


@app.get("/api/analytics/video-stats")
async def get_video_stats(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    days: int = Query(7, ge=1, le=365),
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    collection_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """Get video stats with performance indicators"""

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Query videos in date range
    query = db.query(Video).filter(
        Video.posted_at.isnot(None),
        Video.posted_at >= start_date,
        Video.posted_at <= end_date
    )

    # Apply collection filter
    query = apply_collection_filter(query, collection_id, db)

    # Apply platform filter
    if platform:
        platforms = [p.strip().lower() for p in platform.split(',')]
        query = query.filter(Video.platform.in_(platforms))

    # Apply metric type filter
    if metric_type == "organic":
        query = query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        query = query.filter(Video.is_spark_ad == True)

    videos = query.order_by(Video.views.desc()).offset(offset).limit(limit).all()

    if not videos:
        return []

    # Calculate average views for baseline (using same filter and date range)
    all_videos_query = db.query(Video).filter(
        Video.posted_at.isnot(None),
        Video.posted_at >= start_date,
        Video.posted_at <= end_date
    )
    # Apply collection filter
    all_videos_query = apply_collection_filter(all_videos_query, collection_id, db)

    if platform:
        platforms = [p.strip().lower() for p in platform.split(',')]
        all_videos_query = all_videos_query.filter(Video.platform.in_(platforms))
    if metric_type == "organic":
        all_videos_query = all_videos_query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        all_videos_query = all_videos_query.filter(Video.is_spark_ad == True)
    all_videos = all_videos_query.all()
    if not all_videos:
        avg_views = 0
    else:
        avg_views = sum(v.views for v in all_videos) / len(all_videos)

    result = []
    for video in videos:
        # Calculate performance multiplier
        if avg_views > 0:
            performance_multiplier = video.views / avg_views
        else:
            performance_multiplier = 1

        # Calculate engagement rate
        if video.views > 0:
            engagement_rate = ((video.likes + video.comments + video.shares) / video.views) * 100
        else:
            engagement_rate = 0

        result.append({
            "id": video.id,
            "platform": video.platform,
            "url": video.url,
            "thumbnail": video.thumbnail,
            "caption": video.caption,
            "author_username": video.author_username,
            "author_nickname": video.author_nickname,
            "views": video.views,
            "likes": video.likes,
            "comments": video.comments,
            "shares": video.shares,
            "saves": video.bookmarks or 0,
            "engagement_rate": round(engagement_rate, 2),
            "performance_multiplier": round(performance_multiplier, 1),
            "performance_indicator": f"{performance_multiplier:.1f}x more than usual" if performance_multiplier > 1 else "Below average",
            "posted_at": video.posted_at,
            "scraped_at": video.scraped_at
        })

    return result


# ============ COLLECTIONS ENDPOINTS ============

class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = '#8B5CF6'
    icon: Optional[str] = 'folder'


class CollectionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: str
    icon: str
    is_default: bool
    video_count: int
    account_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@app.get("/api/collections", response_model=List[CollectionResponse])
async def get_collections(db: Session = Depends(get_db)):
    """Get all collections with optimized query (single DB call instead of N+1)"""
    # Single query with LEFT JOIN and GROUP BY to get counts efficiently
    collections_query = db.query(
        Collection,
        func.count(distinct(VideoCollection.video_id)).label('video_count'),
        func.count(distinct(AccountCollection.account_id)).label('account_count')
    ).outerjoin(
        VideoCollection, Collection.id == VideoCollection.collection_id
    ).outerjoin(
        AccountCollection, Collection.id == AccountCollection.collection_id
    ).group_by(Collection.id).order_by(
        Collection.is_default.desc(),
        Collection.created_at.desc()
    ).all()

    # Map results to collection objects with counts
    result = []
    for collection_obj, video_count, account_count in collections_query:
        collection_obj.video_count = video_count
        collection_obj.account_count = account_count
        result.append(collection_obj)

    return result


@app.post("/api/collections", response_model=CollectionResponse)
async def create_collection(
    collection: CollectionCreate,
    db: Session = Depends(get_db)
):
    """Create a new collection"""

    # Check if collection with same name exists
    existing = db.query(Collection).filter(Collection.name == collection.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Collection with this name already exists")

    new_collection = Collection(**collection.dict())
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)

    return new_collection


@app.get("/api/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: int, db: Session = Depends(get_db)):
    """Get a specific collection"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # Update counts
    collection.video_count = db.query(VideoCollection).filter(VideoCollection.collection_id == collection.id).count()
    collection.account_count = db.query(AccountCollection).filter(AccountCollection.collection_id == collection.id).count()
    db.commit()

    return collection


@app.put("/api/collections/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: int,
    collection_data: CollectionCreate,
    db: Session = Depends(get_db)
):
    """Update a collection"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    for key, value in collection_data.dict().items():
        setattr(collection, key, value)

    db.commit()
    db.refresh(collection)

    return collection


@app.delete("/api/collections/{collection_id}")
async def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    """Delete a collection"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if collection.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default collection")

    db.delete(collection)
    db.commit()

    return {"message": "Collection deleted successfully"}


@app.get("/api/collections/{collection_id}/videos", response_model=List[VideoResponse])
async def get_collection_videos(
    collection_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all videos in a collection"""
    video_ids = db.query(VideoCollection.video_id).filter(
        VideoCollection.collection_id == collection_id
    ).offset(offset).limit(limit).all()

    video_ids = [v[0] for v in video_ids]

    videos = db.query(Video).filter(Video.id.in_(video_ids)).all()
    return videos


@app.post("/api/collections/{collection_id}/videos/{video_id}")
async def add_video_to_collection(
    collection_id: int,
    video_id: str,
    db: Session = Depends(get_db)
):
    """Add a video to a collection"""

    # Check if collection exists
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # Check if video exists
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Check if already in collection
    existing = db.query(VideoCollection).filter(
        VideoCollection.video_id == video_id,
        VideoCollection.collection_id == collection_id
    ).first()

    if existing:
        return {"message": "Video already in collection"}

    # Add to collection
    video_collection = VideoCollection(video_id=video_id, collection_id=collection_id)
    db.add(video_collection)
    db.commit()

    return {"message": "Video added to collection successfully"}


@app.delete("/api/collections/{collection_id}/videos/{video_id}")
async def remove_video_from_collection(
    collection_id: int,
    video_id: str,
    db: Session = Depends(get_db)
):
    """Remove a video from a collection"""

    video_collection = db.query(VideoCollection).filter(
        VideoCollection.video_id == video_id,
        VideoCollection.collection_id == collection_id
    ).first()

    if not video_collection:
        raise HTTPException(status_code=404, detail="Video not in this collection")

    db.delete(video_collection)
    db.commit()

    return {"message": "Video removed from collection successfully"}


@app.get("/api/collections/{collection_id}/accounts")
async def get_collection_accounts(
    collection_id: int,
    db: Session = Depends(get_db)
):
    """Get all accounts in a collection"""
    account_ids = db.query(AccountCollection.account_id).filter(
        AccountCollection.collection_id == collection_id
    ).all()

    account_ids_list = [aid[0] for aid in account_ids]
    accounts = db.query(Account).filter(Account.id.in_(account_ids_list)).all()

    return accounts


@app.post("/api/collections/{collection_id}/accounts/{account_id}")
async def add_account_to_collection(
    collection_id: int,
    account_id: int,
    db: Session = Depends(get_db)
):
    """Add an account to a collection"""

    # Check if collection exists
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # Check if account exists
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Check if already in collection
    existing = db.query(AccountCollection).filter(
        AccountCollection.account_id == account_id,
        AccountCollection.collection_id == collection_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Account already in this collection")

    # Add to collection
    account_collection = AccountCollection(
        account_id=account_id,
        collection_id=collection_id
    )
    db.add(account_collection)
    db.commit()

    return {"message": "Account added to collection successfully"}


@app.delete("/api/collections/{collection_id}/accounts/{account_id}")
async def remove_account_from_collection(
    collection_id: int,
    account_id: int,
    db: Session = Depends(get_db)
):
    """Remove an account from a collection"""

    account_collection = db.query(AccountCollection).filter(
        AccountCollection.account_id == account_id,
        AccountCollection.collection_id == collection_id
    ).first()

    if not account_collection:
        raise HTTPException(status_code=404, detail="Account not in this collection")

    db.delete(account_collection)
    db.commit()

    return {"message": "Account removed from collection successfully"}


# ============ ACCOUNTS ENDPOINTS ============

class AccountResponse(BaseModel):
    id: int
    username: str
    platform: str
    nickname: Optional[str]
    avatar: Optional[str]
    bio: Optional[str]
    profile_url: Optional[str]
    total_videos: int
    total_views: int
    total_likes: int
    total_followers: int
    is_verified: bool
    is_active: bool
    first_tracked: datetime
    last_scraped: datetime

    class Config:
        from_attributes = True


@app.get("/api/accounts", response_model=List[AccountResponse])
async def get_accounts(
    platform: Optional[str] = None,
    collection_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all tracked accounts"""

    if collection_id:
        # Get accounts in specific collection
        account_ids = db.query(AccountCollection.account_id).filter(
            AccountCollection.collection_id == collection_id
        ).all()
        account_ids = [a[0] for a in account_ids]

        query = db.query(Account).filter(
            Account.id.in_(account_ids),
            Account.is_active == True  # Only show active accounts
        )
    else:
        query = db.query(Account).filter(Account.is_active == True)  # Only show active accounts

    if platform:
        query = query.filter(Account.platform == platform)

    accounts = query.order_by(Account.total_views.desc()).offset(offset).limit(limit).all()
    return accounts


class AccountCreate(BaseModel):
    username: str
    platform: str
    profile_url: str
    nickname: Optional[str] = None


@app.post("/api/accounts", response_model=AccountResponse)
async def create_account(account_data: AccountCreate, db: Session = Depends(get_db)):
    """Create a new account to track"""

    # Check if account already exists
    existing = db.query(Account).filter(
        Account.username == account_data.username,
        Account.platform == account_data.platform
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Account already exists")

    # Create new account
    account = Account(
        username=account_data.username,
        platform=account_data.platform,
        profile_url=account_data.profile_url,
        nickname=account_data.nickname or account_data.username,
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, db: Session = Depends(get_db)):
    """Get a specific account"""
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@app.get("/api/accounts/{account_id}/videos", response_model=List[VideoResponse])
async def get_account_videos(
    account_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all videos from an account"""

    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    videos = db.query(Video).filter(
        Video.author_username == account.username,
        Video.platform == account.platform
    ).order_by(Video.scraped_at.desc()).offset(offset).limit(limit).all()

    return videos


@app.post("/api/accounts/{account_id}/refresh")
async def refresh_account(account_id: int, db: Session = Depends(get_db)):
    """Refresh account stats by aggregating from videos"""

    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Get all videos from this account
    videos = db.query(Video).filter(
        Video.author_username == account.username,
        Video.platform == account.platform
    ).all()

    # Aggregate stats
    account.total_videos = len(videos)
    account.total_views = sum(v.views for v in videos)
    account.total_likes = sum(v.likes for v in videos)
    account.last_scraped = datetime.utcnow()

    db.commit()
    db.refresh(account)

    return account


@app.delete("/api/accounts/{account_id}")
async def delete_account(
    account_id: str,
    db: Session = Depends(get_db)
):
    """
    Soft delete an account (set is_active = False)
    This hides the account and its videos from all views
    """
    # Find the account
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Soft delete
    account.is_active = False

    # Remove from all collections
    db.query(AccountCollection).filter(AccountCollection.account_id == account_id).delete()

    # Update collection account counts
    collections = db.query(Collection).all()
    for collection in collections:
        collection.account_count = db.query(AccountCollection).filter(
            AccountCollection.collection_id == collection.id
        ).count()

    db.commit()

    return {
        "message": f"Account {account.username} deleted successfully",
        "account_id": account_id
    }


@app.post("/api/admin/seed-accounts")
async def seed_accounts(db: Session = Depends(get_db)):
    """Seed database with initial accounts"""
    accounts_data = [
        # Original TikTok accounts
        {"username": "professorcuriousaapp", "platform": "tiktok", "nickname": "Professor Curious"},
        {"username": "rose.studycorner", "platform": "tiktok", "nickname": "Rose Study Corner"},
        {"username": "piaprofessor", "platform": "tiktok", "nickname": "Pia Professor"},
        {"username": "succeedwjoseph", "platform": "tiktok", "nickname": "Succeed with Joseph"},
        {"username": "mari.curious", "platform": "tiktok", "nickname": "Mari Curious"},
        {"username": "max.curious1", "platform": "tiktok", "nickname": "Max Curious"},
        {"username": "karissa.curious", "platform": "tiktok", "nickname": "Karissa Curious"},
        # Chloe
        {"username": "midn1ghtnova", "platform": "tiktok", "nickname": "Chloe"},
        {"username": "midn1ghtnova1", "platform": "instagram", "nickname": "Chloe"},
        # Sarah
        {"username": "waithearmeout46", "platform": "tiktok", "nickname": "Sarah"},
        {"username": "waithearmeout46", "platform": "instagram", "nickname": "Sarah"},
        # Arshia
        {"username": "swagdivafineshyt67", "platform": "tiktok", "nickname": "Arshia"},
        {"username": "swagdivafineshyt67", "platform": "instagram", "nickname": "Arshia"},
    ]

    added = []
    skipped = []

    for account_data in accounts_data:
        # Check if already exists
        existing = db.query(Account).filter(
            Account.username == account_data['username'],
            Account.platform == account_data['platform']
        ).first()

        if existing:
            skipped.append(f"{account_data['platform']}/@{account_data['username']}")
            continue

        # Create profile URL
        profile_url = f"https://www.{account_data['platform']}.com/@{account_data['username']}"

        # Create new account
        account = Account(
            platform=account_data['platform'],
            username=account_data['username'],
            profile_url=profile_url,
            nickname=account_data['nickname'],
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.add(account)
        added.append(f"{account_data['platform']}/@{account_data['username']}")

    db.commit()

    return {
        "added": added,
        "skipped": skipped,
        "total_added": len(added),
        "total_skipped": len(skipped)
    }


# ============ DAILY SCRAPING SCHEDULER ============

def daily_scrape_all_accounts():
    """
    Daily job to re-scrape all active accounts and save historical snapshots.
    This runs automatically once per day to track growth over time.
    """
    logger.info("Starting daily scrape of all active accounts...")

    from database import SessionLocal
    db = SessionLocal()

    try:
        # Get all active accounts
        accounts = db.query(Account).filter(Account.is_active == True).all()
        logger.info(f"Found {len(accounts)} active accounts to scrape")

        scraper = URLScraper()
        total_videos = 0

        for account in accounts:
            try:
                # Construct profile URL
                if account.platform == 'tiktok':
                    url = f"https://www.tiktok.com/@{account.username}"
                elif account.platform == 'instagram':
                    url = f"https://www.instagram.com/{account.username}/"
                else:
                    logger.warning(f"Unsupported platform {account.platform} for account {account.username}")
                    continue

                logger.info(f"Scraping {account.platform}/@{account.username}...")

                # Scrape account
                videos = scraper.scrape_url(url)

                if videos:
                    # Process each video
                    for video_data in videos:
                        # Check if video exists
                        video = db.query(Video).filter(Video.id == video_data['id']).first()

                        if video:
                            # Update existing video metrics
                            video.views = video_data.get('views', video.views)
                            video.likes = video_data.get('likes', video.likes)
                            video.comments = video_data.get('comments', video.comments)
                            video.shares = video_data.get('shares', video.shares)
                            video.scraped_at = datetime.utcnow()

                            # Save daily snapshot
                            save_video_snapshot(db, video)
                            total_videos += 1
                        else:
                            # Create new video if not exists
                            new_video = Video(**video_data)
                            db.add(new_video)
                            db.commit()
                            db.refresh(new_video)

                            # Save initial snapshot
                            save_video_snapshot(db, new_video)
                            total_videos += 1

                    # Update account last_scraped timestamp
                    account.last_scraped = datetime.utcnow()
                    db.commit()

                    logger.info(f"✓ Scraped {len(videos)} videos from {account.platform}/@{account.username}")
                else:
                    logger.warning(f"No videos found for {account.platform}/@{account.username}")

            except Exception as e:
                logger.error(f"Error scraping {account.platform}/@{account.username}: {str(e)}")
                continue

        logger.info(f"Daily scrape completed! Updated {total_videos} videos across {len(accounts)} accounts")

    except Exception as e:
        logger.error(f"Error in daily scrape job: {str(e)}")
    finally:
        db.close()


@app.post("/api/admin/fix-missing-accounts")
async def fix_missing_accounts(db: Session = Depends(get_db)):
    """
    Fix missing accounts - Create account entities for videos that don't have associated accounts.
    This fixes the bug where videos are saved but accounts aren't created during background scraping.
    """
    try:
        # Get all unique (author_username, platform) combinations from videos
        videos = db.query(Video).all()

        unique_authors = {}
        for video in videos:
            if video.author_username:
                key = (video.author_username, video.platform)
                if key not in unique_authors:
                    unique_authors[key] = video

        # Check which ones don't have accounts
        missing_accounts = []
        created_accounts = []

        for (username, platform), video in unique_authors.items():
            account = db.query(Account).filter(
                Account.username == username,
                Account.platform == platform
            ).first()

            if not account:
                missing_accounts.append((username, platform, video))

        logger.info(f"Found {len(missing_accounts)} accounts that need to be created")

        if missing_accounts:
            for username, platform, video in missing_accounts:
                # Get all videos for this account to calculate aggregate stats
                account_videos = db.query(Video).filter(
                    Video.author_username == username,
                    Video.platform == platform
                ).all()

                total_videos = len(account_videos)
                total_views = sum(v.views or 0 for v in account_videos)
                total_likes = sum(v.likes or 0 for v in account_videos)

                # Create account with aggregated stats
                account = Account(
                    username=username,
                    platform=platform,
                    nickname=video.author_nickname,
                    avatar=video.author_avatar,
                    profile_url=f"https://www.tiktok.com/@{username}" if platform == 'tiktok' else f"https://www.instagram.com/{username}/",
                    total_videos=total_videos,
                    total_views=total_views,
                    total_likes=total_likes,
                    total_followers=0,
                    is_active=True,
                    last_scraped=datetime.utcnow()
                )
                db.add(account)
                created_accounts.append({
                    "username": username,
                    "platform": platform,
                    "total_videos": total_videos,
                    "total_views": total_views
                })

                logger.info(f"Created account: {platform}/@{username} with {total_videos} videos")

            db.commit()
            logger.info(f"Successfully created {len(created_accounts)} missing accounts")

        return {
            "status": "success",
            "message": f"Created {len(created_accounts)} missing accounts",
            "accounts_created": len(created_accounts),
            "created": created_accounts
        }

    except Exception as e:
        logger.error(f"Error fixing missing accounts: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler on startup"""
    logger.info("Starting up application...")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Schedule daily scraping at 2 AM UTC every day
    scheduler.add_job(
        daily_scrape_all_accounts,
        CronTrigger(hour=2, minute=0),  # Run at 2:00 AM UTC daily
        id='daily_scrape_job',
        name='Daily account scraping',
        replace_existing=True
    )

    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started - daily scraping will run at 2:00 AM UTC")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown scheduler gracefully"""
    logger.info("Shutting down scheduler...")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


@app.post("/api/admin/daily-scrape")
async def trigger_daily_scrape(background_tasks: BackgroundTasks):
    """
    Manually trigger the daily scraping job.
    Use this endpoint to test or force a daily scrape without waiting for the scheduled time.
    """
    background_tasks.add_task(daily_scrape_all_accounts)
    return {
        "status": "started",
        "message": "Daily scraping job started in background. This will re-scrape all active accounts and update historical data."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
