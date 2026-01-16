from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import get_db, init_db, Video, TrendingAudio, Hashtag, SearchHistory, ScrapingJob, Collection, Account, VideoCollection, AccountCollection
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
    """Get list of unique creators/authors from videos"""

    from sqlalchemy import func

    query = db.query(
        Video.author_username,
        func.max(Video.author_nickname).label('author_nickname')
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
    days: int = Query(7, ge=1, le=90),
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
        # Update last_scraped
        account.last_scraped = datetime.utcnow()
        account.avatar = video.author_avatar or account.avatar
        account.nickname = video.author_nickname or account.nickname
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
            total_followers=0
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


@app.post("/api/scrape/urls", response_model=List[URLScrapeResponse])
async def scrape_urls(
    request: URLScrapeRequest,
    db: Session = Depends(get_db)
):
    """Scrape video metrics from URLs (supports both individual videos and profile URLs)"""

    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

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
        for url in request.urls:
            try:
                # Detect if this is a profile or video URL
                url_type = scraper.detect_url_type(url)

                if url_type == 'profile':
                    # Scrape all videos from profile
                    profile_data = await scraper.scrape_profile(url, limit=100)

                    # Save all videos from profile to database
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

    if errors and not results:
        # All URLs failed
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape all URLs. Errors: {errors}"
        )

    # Return results even if some failed
    return results


@app.get("/api/analytics/overview")
async def get_analytics_overview(
    days: int = Query(7, ge=1, le=90),
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get analytics overview for metrics cards"""

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Query videos in date range
    query = db.query(Video).filter(Video.scraped_at >= start_date)

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

    videos = query.all()

    if not videos:
        return {
            "views": {"total": 0, "change": 0},
            "engagement": {"total": 0, "change": 0},
            "likes": {"total": 0, "change": 0},
            "comments": {"total": 0, "change": 0},
            "shares": {"total": 0, "change": 0},
            "saves": {"total": 0, "change": 0}
        }

    # Calculate totals
    total_views = sum(v.views for v in videos)
    total_likes = sum(v.likes for v in videos)
    total_comments = sum(v.comments for v in videos)
    total_shares = sum(v.shares for v in videos)
    total_bookmarks = sum(v.bookmarks or 0 for v in videos)
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
    days: int = Query(7, ge=1, le=90),
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get cumulative views over time based on video posted dates"""

    # Get all videos with posted_at dates
    query = db.query(Video).filter(Video.posted_at.isnot(None))

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

    # Find the date range from actual video data
    earliest_date = min(v.posted_at for v in videos if v.posted_at)
    latest_date = max(v.posted_at for v in videos if v.posted_at)

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


@app.get("/api/analytics/most-viral")
async def get_most_viral_videos(
    limit: int = Query(10, ge=1, le=50),
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get most viral videos based on engagement rate"""

    query = db.query(Video)

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
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get virality median analysis data"""

    query = db.query(Video)

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
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get duration analysis data"""

    query = db.query(Video).filter(Video.duration != None)

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

    # Daily videos query
    daily_query = db.query(Video).filter(Video.scraped_at >= one_day_ago)
    if platform:
        platforms = [p.strip().upper() for p in platform.split(',')]
        daily_query = daily_query.filter(Video.platform.in_(platforms))
    if metric_type == "organic":
        daily_query = daily_query.filter(Video.is_spark_ad == False)
    elif metric_type == "ads":
        daily_query = daily_query.filter(Video.is_spark_ad == True)
    daily_videos = daily_query.all()

    # Weekly videos query
    weekly_query = db.query(Video).filter(Video.scraped_at >= seven_days_ago)
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
    metric_type: str = Query("total", regex="^(total|organic|ads)$"),
    platform: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get video stats with performance indicators"""

    query = db.query(Video)

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

    # Calculate average views for baseline (using same filter)
    all_videos_query = db.query(Video)
    if platform:
        platforms = [p.strip().upper() for p in platform.split(',')]
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
    """Get all collections"""
    collections = db.query(Collection).order_by(Collection.is_default.desc(), Collection.created_at.desc()).all()

    # Update counts
    for collection in collections:
        collection.video_count = db.query(VideoCollection).filter(VideoCollection.collection_id == collection.id).count()
        collection.account_count = db.query(AccountCollection).filter(AccountCollection.collection_id == collection.id).count()

    db.commit()
    return collections


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

        query = db.query(Account).filter(Account.id.in_(account_ids))
    else:
        query = db.query(Account)

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
