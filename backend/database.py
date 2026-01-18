from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Float, DateTime, JSON, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://anubhavmishra@localhost:5432/social_media_tracker")

# For local development, use SQLite if PostgreSQL fails
engine = None
try:
    engine = create_engine(DATABASE_URL)
    # Test connection
    conn = engine.connect()
    conn.close()
    print("Connected to PostgreSQL database")
except Exception as e:
    print(f"PostgreSQL connection failed: {e}")
    print("Using SQLite for local development")
    DATABASE_URL = "sqlite:///./social_media_tracker.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    platform = Column(String, nullable=False, index=True)  # tiktok, youtube, instagram
    url = Column(String, nullable=False)
    thumbnail = Column(String)
    caption = Column(Text)

    # Author info
    author_username = Column(String, index=True)
    author_nickname = Column(String)
    author_avatar = Column(String)
    author_id = Column(String, index=True)

    # Stats
    views = Column(BigInteger, default=0)
    likes = Column(BigInteger, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    bookmarks = Column(Integer, default=0)  # TikTok bookmarks/saves
    is_spark_ad = Column(Boolean, default=False, nullable=False)  # Track if video is a Spark Ad (paid promotion)
    installs = Column(Integer, default=0)  # App installs from video
    trial_started = Column(Integer, default=0)  # Trial subscriptions started from video

    # Music/Audio
    music_id = Column(String, index=True)
    music_title = Column(String)
    music_author = Column(String)
    music_url = Column(String)

    # Metadata
    hashtags = Column(JSON)  # Array of hashtags
    mentions = Column(JSON)  # Array of mentioned users
    duration = Column(Integer)  # Video duration in seconds

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    posted_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_platform_scraped', 'platform', 'scraped_at'),
        Index('idx_music_platform', 'music_id', 'platform'),
    )


class VideoHistory(Base):
    """Store daily snapshots of video metrics for tracking growth over time"""
    __tablename__ = "video_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False)

    # Snapshot metrics
    views = Column(BigInteger, default=0)
    likes = Column(BigInteger, default=0)
    comments = Column(BigInteger, default=0)
    shares = Column(BigInteger, default=0)
    saves = Column(BigInteger, default=0)

    # Calculated growth (vs previous day)
    views_growth = Column(BigInteger, default=0)
    likes_growth = Column(BigInteger, default=0)
    comments_growth = Column(BigInteger, default=0)

    # Timestamp for this snapshot
    snapshot_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_video_snapshot', 'video_id', 'platform', 'snapshot_date'),
    )


class TrendingAudio(Base):
    __tablename__ = "trending_audio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    music_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False, default='tiktok')

    # Audio info
    title = Column(String, nullable=False)
    author = Column(String)
    play_url = Column(String)
    thumbnail = Column(String)

    # Stats
    total_videos = Column(BigInteger, default=0)
    total_views = Column(BigInteger, default=0)
    rank = Column(Integer)

    # Location
    country = Column(String, index=True)  # US, UK, IN, etc.

    # Sample videos using this audio
    sample_video_ids = Column(JSON)  # Array of video IDs

    # Timestamps
    trending_date = Column(DateTime, default=datetime.utcnow, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_country_trending', 'country', 'trending_date'),
        Index('idx_music_country', 'music_id', 'country'),
    )


class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False)

    # Stats
    total_videos = Column(BigInteger, default=0)
    total_views = Column(BigInteger, default=0)

    # Metadata
    description = Column(Text)

    # Timestamps
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_hashtag_platform', 'name', 'platform'),
    )


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String, nullable=False, index=True)
    query_type = Column(String, nullable=False)  # hashtag, term, audio
    platform = Column(String, nullable=False)
    country = Column(String)

    # Results
    results_count = Column(Integer, default=0)

    # Timestamps
    searched_at = Column(DateTime, default=datetime.utcnow, index=True)


class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_type = Column(String, nullable=False)  # hashtag_search, trending_audio
    platform = Column(String, nullable=False)
    query = Column(String)
    country = Column(String)

    # Status
    status = Column(String, default='pending')  # pending, running, completed, failed
    progress = Column(Integer, default=0)
    total = Column(Integer, default=0)
    error_message = Column(Text)

    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class Account(Base):
    """Track TikTok/YouTube/Instagram accounts separately"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False, index=True)  # tiktok, youtube, instagram

    # Profile info
    nickname = Column(String)
    avatar = Column(String)
    bio = Column(Text)
    profile_url = Column(String)

    # Stats (aggregated from videos)
    total_videos = Column(Integer, default=0)
    total_views = Column(BigInteger, default=0)
    total_likes = Column(BigInteger, default=0)
    total_followers = Column(BigInteger, default=0)

    # Metadata
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # User can mark as inactive

    # Timestamps
    first_tracked = Column(DateTime, default=datetime.utcnow)
    last_scraped = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_username_platform', 'username', 'platform'),
    )


class Collection(Base):
    """Collections to organize videos and accounts"""
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)

    # Metadata
    color = Column(String, default='#8B5CF6')  # Purple default
    icon = Column(String, default='folder')
    is_default = Column(Boolean, default=False)

    # Stats (auto-calculated)
    video_count = Column(Integer, default=0)
    account_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VideoCollection(Base):
    """Many-to-many relationship between videos and collections"""
    __tablename__ = "video_collections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, ForeignKey('videos.id', ondelete='CASCADE'), nullable=False)
    collection_id = Column(Integer, ForeignKey('collections.id', ondelete='CASCADE'), nullable=False)

    # Metadata
    added_at = Column(DateTime, default=datetime.utcnow)
    added_by = Column(String)  # For future user system

    __table_args__ = (
        Index('idx_video_collection', 'video_id', 'collection_id'),
        Index('idx_collection_videos', 'collection_id', 'added_at'),
    )


class AccountCollection(Base):
    """Many-to-many relationship between accounts and collections"""
    __tablename__ = "account_collections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False)
    collection_id = Column(Integer, ForeignKey('collections.id', ondelete='CASCADE'), nullable=False)

    # Metadata
    added_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_account_collection', 'account_id', 'collection_id'),
    )


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
