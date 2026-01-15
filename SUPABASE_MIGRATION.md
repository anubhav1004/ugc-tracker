# Supabase Migration Guide

## Overview

This guide explains how to migrate from PostgreSQL to Supabase. The current backend uses SQLAlchemy ORM with PostgreSQL, which is fully compatible with Supabase (which is built on PostgreSQL).

## Database Schema

### Core Tables

#### 1. `videos` - Main video tracking table
```sql
CREATE TABLE videos (
    id VARCHAR PRIMARY KEY,
    platform VARCHAR NOT NULL,
    url VARCHAR NOT NULL,
    thumbnail VARCHAR,
    caption TEXT,

    -- Author info
    author_username VARCHAR,
    author_nickname VARCHAR,
    author_avatar VARCHAR,
    author_id VARCHAR,

    -- Stats
    views BIGINT DEFAULT 0,
    likes BIGINT DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    bookmarks INTEGER DEFAULT 0,

    -- Music/Audio
    music_id VARCHAR,
    music_title VARCHAR,
    music_author VARCHAR,
    music_url VARCHAR,

    -- Metadata
    hashtags JSONB,
    mentions JSONB,
    duration INTEGER,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    posted_at TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_platform ON videos(platform);
CREATE INDEX idx_author_username ON videos(author_username);
CREATE INDEX idx_author_id ON videos(author_id);
CREATE INDEX idx_music_id ON videos(music_id);
CREATE INDEX idx_scraped_at ON videos(scraped_at);
CREATE INDEX idx_platform_scraped ON videos(platform, scraped_at);
CREATE INDEX idx_music_platform ON videos(music_id, platform);
```

#### 2. `accounts` - Creator/Account tracking
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,

    -- Profile info
    nickname VARCHAR,
    avatar VARCHAR,
    bio TEXT,
    profile_url VARCHAR,

    -- Stats (aggregated from videos)
    total_videos INTEGER DEFAULT 0,
    total_views BIGINT DEFAULT 0,
    total_likes BIGINT DEFAULT 0,
    total_followers BIGINT DEFAULT 0,

    -- Metadata
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    first_tracked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_username_platform ON accounts(username, platform);
```

#### 3. `collections` - Organize videos and accounts
```sql
CREATE TABLE collections (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,

    -- Metadata
    color VARCHAR DEFAULT '#8B5CF6',
    icon VARCHAR DEFAULT 'folder',
    is_default BOOLEAN DEFAULT FALSE,

    -- Stats (auto-calculated)
    video_count INTEGER DEFAULT 0,
    account_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_collection_name ON collections(name);
CREATE INDEX idx_is_default ON collections(is_default);
```

#### 4. `video_collections` - Many-to-many relationship
```sql
CREATE TABLE video_collections (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR REFERENCES videos(id) ON DELETE CASCADE,
    collection_id INTEGER REFERENCES collections(id) ON DELETE CASCADE,

    -- Metadata
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by VARCHAR
);

CREATE INDEX idx_video_collection ON video_collections(video_id, collection_id);
CREATE INDEX idx_collection_videos ON video_collections(collection_id, added_at);
```

#### 5. `account_collections` - Account to collection mapping
```sql
CREATE TABLE account_collections (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    collection_id INTEGER REFERENCES collections(id) ON DELETE CASCADE,

    -- Metadata
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_account_collection ON account_collections(account_id, collection_id);
```

### Supporting Tables

#### 6. `trending_audio` - Track trending sounds
```sql
CREATE TABLE trending_audio (
    id SERIAL PRIMARY KEY,
    music_id VARCHAR NOT NULL,
    platform VARCHAR NOT NULL DEFAULT 'tiktok',

    -- Audio info
    title VARCHAR NOT NULL,
    author VARCHAR,
    play_url VARCHAR,
    thumbnail VARCHAR,

    -- Stats
    total_videos BIGINT DEFAULT 0,
    total_views BIGINT DEFAULT 0,
    rank INTEGER,

    -- Location
    country VARCHAR,

    -- Sample videos
    sample_video_ids JSONB,

    -- Timestamps
    trending_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_music_id ON trending_audio(music_id);
CREATE INDEX idx_country ON trending_audio(country);
CREATE INDEX idx_trending_date ON trending_audio(trending_date);
CREATE INDEX idx_country_trending ON trending_audio(country, trending_date);
CREATE INDEX idx_music_country ON trending_audio(music_id, country);
```

#### 7. `hashtags` - Track hashtag usage
```sql
CREATE TABLE hashtags (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,

    -- Stats
    total_videos BIGINT DEFAULT 0,
    total_views BIGINT DEFAULT 0,

    -- Metadata
    description TEXT,

    -- Timestamps
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hashtag_name ON hashtags(name);
CREATE INDEX idx_hashtag_platform ON hashtags(name, platform);
```

#### 8. `search_history` - Log all searches
```sql
CREATE TABLE search_history (
    id SERIAL PRIMARY KEY,
    query VARCHAR NOT NULL,
    query_type VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,
    country VARCHAR,

    -- Results
    results_count INTEGER DEFAULT 0,

    -- Timestamps
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_query ON search_history(query);
CREATE INDEX idx_searched_at ON search_history(searched_at);
```

#### 9. `scraping_jobs` - Track scraping tasks
```sql
CREATE TABLE scraping_jobs (
    id SERIAL PRIMARY KEY,
    job_type VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,
    query VARCHAR,
    country VARCHAR,

    -- Status
    status VARCHAR DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    total INTEGER DEFAULT 0,
    error_message TEXT,

    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Migration Steps

### 1. Set Up Supabase

1. Create a new Supabase project at https://supabase.com
2. Get your database connection string from Settings > Database
3. Note your API keys (anon/public and service_role)

### 2. Run Database Schema

Execute the SQL schemas above in Supabase SQL Editor in this order:
1. `videos`
2. `accounts`
3. `collections`
4. `video_collections`
5. `account_collections`
6. `trending_audio`
7. `hashtags`
8. `search_history`
9. `scraping_jobs`

### 3. Create Default Collection

```sql
INSERT INTO collections (name, description, is_default, color)
VALUES ('Default', 'All tracked videos', TRUE, '#8B5CF6');
```

### 4. Update Backend Configuration

Update `.env` file:

```env
# Replace with your Supabase connection string
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres

# Optional: Supabase API keys for future features
SUPABASE_URL=https://[PROJECT_ID].supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
```

### 5. Enable Row Level Security (RLS) - Optional

For production, enable RLS on tables:

```sql
-- Example: Enable RLS on videos table
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;

-- Create policy (adjust based on your auth needs)
CREATE POLICY "Allow all operations for now"
ON videos FOR ALL
USING (true);
```

## API Endpoints Reference

### Collections

- `GET /api/collections` - List all collections
- `POST /api/collections` - Create collection
- `GET /api/collections/{id}` - Get collection
- `PUT /api/collections/{id}` - Update collection
- `DELETE /api/collections/{id}` - Delete collection
- `GET /api/collections/{id}/videos` - Get videos in collection
- `POST /api/collections/{id}/videos/{video_id}` - Add video to collection
- `DELETE /api/collections/{id}/videos/{video_id}` - Remove video from collection

### Accounts

- `GET /api/accounts` - List all accounts
- `GET /api/accounts?platform=tiktok` - Filter by platform
- `GET /api/accounts?collection_id=1` - Filter by collection
- `GET /api/accounts/{id}` - Get account
- `GET /api/accounts/{id}/videos` - Get account videos
- `POST /api/accounts/{id}/refresh` - Refresh account stats

### Videos

- `POST /api/scrape/urls` - Add videos by URL
- `GET /api/videos` - List videos
- `GET /api/videos/{id}` - Get video
- `GET /api/stats` - Get overall stats

### Analytics

- `GET /api/analytics/overview` - Metrics cards data
- `GET /api/analytics/views-over-time` - Views chart
- `GET /api/analytics/most-viral` - Top videos
- `GET /api/analytics/virality-analysis` - Virality distribution
- `GET /api/analytics/duration-analysis` - Duration analysis
- `GET /api/analytics/metrics-breakdown` - Daily/weekly averages
- `GET /api/analytics/video-stats` - Video performance table

## Backend Features

### ✅ Implemented

1. **Video Scraping**
   - TikTok video URLs
   - TikTok profile URLs (scrapes all videos)
   - YouTube video search
   - Automatic account creation

2. **Collections Management**
   - Create/update/delete collections
   - Add/remove videos from collections
   - Auto-create default collection
   - Track video counts

3. **Account Tracking**
   - Auto-create accounts from videos
   - Aggregate stats (views, likes, videos)
   - Profile information
   - Last scraped tracking

4. **Analytics**
   - Overview metrics (7/30/90 days)
   - Views over time
   - Virality analysis
   - Duration analysis
   - Performance indicators

5. **Scrapers**
   - TikTok API (Playwright-based)
   - YouTube search API
   - Trending audio tracker
   - Profile scraper

### 🔄 Ready for Enhancement

1. **User Authentication** (prepare for Supabase Auth)
2. **Real-time Updates** (Supabase Realtime)
3. **File Storage** (Supabase Storage for thumbnails)
4. **Scheduled Jobs** (Supabase Edge Functions)

## Data Flow

1. **User adds TikTok URL** → Frontend calls `/api/scrape/urls`
2. **Backend scrapes video** → URL Scraper extracts data
3. **Create/update video** → Save to `videos` table
4. **Create/update account** → Save to `accounts` table
5. **Add to collection** → Create relationship in `video_collections`
6. **Calculate stats** → Update account aggregates
7. **Return to frontend** → Display in dashboard

## Performance Considerations

### Indexes

All tables have appropriate indexes for:
- Primary keys
- Foreign keys
- Frequently queried fields
- Composite indexes for common queries

### Query Optimization

- Use `LIMIT` and `OFFSET` for pagination
- Filter early in queries
- Aggregate stats are cached in account/collection tables
- JSON fields for array data (hashtags, mentions)

### Caching Strategy (Future)

- Cache analytics for 1 hour
- Cache collection counts for 15 minutes
- Use Supabase Realtime for live updates

## Security Notes

### Current Setup (Development)

- No authentication required
- All endpoints publicly accessible
- Suitable for development/testing

### Production Recommendations

1. Enable Supabase Auth
2. Add user_id to all tables
3. Enable RLS policies
4. Validate API inputs
5. Rate limit scraping endpoints
6. Use service_role key for backend only

## Testing the Migration

After migration, test these flows:

```bash
# 1. Check API health
curl http://localhost:8000/

# 2. Test collections
curl http://localhost:8000/api/collections

# 3. Add a video
curl -X POST http://localhost:8000/api/scrape/urls \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.tiktok.com/@username/video/123"]}'

# 4. Check accounts
curl http://localhost:8000/api/accounts

# 5. View analytics
curl http://localhost:8000/api/analytics/overview
```

## Support

For issues during migration:
1. Check Supabase logs in Dashboard > Logs
2. Verify connection string in `.env`
3. Ensure all tables are created
4. Check backend logs: `tail -f backend/backend.log`

## Next Steps After Migration

1. ✅ Migrate database to Supabase
2. Add user authentication (Supabase Auth)
3. Implement Row Level Security
4. Set up scheduled scraping (Edge Functions)
5. Add real-time notifications
6. Optimize with Supabase indexes
7. Deploy backend to cloud (Render/Railway/Vercel)
8. Deploy frontend to Vercel/Netlify

---

**Your backend is now fully ready for Supabase!** Just update the `DATABASE_URL` and you're good to go.
