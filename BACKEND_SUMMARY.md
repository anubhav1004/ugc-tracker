# Backend Summary - Viral Analytics

## 🎯 Complete Backend Implementation

A production-ready FastAPI backend with comprehensive TikTok analytics, collections management, and account tracking.

---

## 📦 Tech Stack

- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL (Supabase-ready)
- **ORM**: SQLAlchemy
- **Scrapers**:
  - TikTok: davidteather/TikTok-Api (Playwright)
  - YouTube: youtube-search-python
  - Custom: Trending audio tracker
- **Async**: asyncio for concurrent operations

---

## 🗄️ Database Schema (9 Tables)

### Core Tables

1. **`videos`** - Main video data
   - Platform (TikTok, YouTube, Instagram)
   - Author info (username, avatar, nickname)
   - Stats (views, likes, comments, shares, bookmarks)
   - Music/audio details
   - Hashtags & mentions (JSON)
   - Timestamps

2. **`accounts`** - Creator tracking
   - Profile information
   - Aggregated stats (total videos, views, likes)
   - Verification status
   - Auto-updated from videos

3. **`collections`** - Organize content
   - Name, description, color, icon
   - Video & account counts
   - Default collection support

4. **`video_collections`** - Many-to-many videos ↔ collections
   - Relationship mapping
   - Added timestamp

5. **`account_collections`** - Many-to-many accounts ↔ collections
   - Relationship mapping

### Supporting Tables

6. **`trending_audio`** - Track trending sounds
   - Country-specific data
   - Rank and total videos
   - Sample video IDs

7. **`hashtags`** - Hashtag statistics
   - Total videos and views
   - Platform tracking

8. **`search_history`** - Query logging
   - Search type and results
   - Analytics tracking

9. **`scraping_jobs`** - Job management
   - Status tracking
   - Progress monitoring
   - Error logging

---

## 🚀 API Endpoints (40+)

### 📹 Video Management

```
POST   /api/scrape/urls              # Add videos by URL (TikTok/YouTube)
GET    /api/videos                   # List all videos (paginated)
GET    /api/videos/{id}              # Get specific video
GET    /api/trending/videos          # Get trending videos
```

**Key Features:**
- ✅ Scrapes TikTok video URLs
- ✅ Scrapes TikTok profile URLs (all videos from account)
- ✅ Auto-creates accounts
- ✅ Auto-adds to default collection
- ✅ Updates existing videos
- ✅ Handles errors gracefully

### 👥 Account Management

```
GET    /api/accounts                 # List all accounts
GET    /api/accounts?platform=tiktok # Filter by platform
GET    /api/accounts?collection_id=1 # Filter by collection
GET    /api/accounts/{id}            # Get specific account
GET    /api/accounts/{id}/videos     # Get account's videos
POST   /api/accounts/{id}/refresh    # Refresh aggregated stats
```

**Auto-Features:**
- ✅ Auto-creates account when video is scraped
- ✅ Auto-updates avatar, nickname
- ✅ Auto-aggregates stats (views, likes, video count)
- ✅ Tracks last scraped timestamp

### 📁 Collections Management

```
GET    /api/collections                         # List all collections
POST   /api/collections                         # Create new collection
GET    /api/collections/{id}                    # Get collection
PUT    /api/collections/{id}                    # Update collection
DELETE /api/collections/{id}                    # Delete collection
GET    /api/collections/{id}/videos             # Get videos in collection
POST   /api/collections/{id}/videos/{video_id}  # Add video to collection
DELETE /api/collections/{id}/videos/{video_id}  # Remove from collection
```

**Features:**
- ✅ Auto-creates "Default" collection on first video
- ✅ Color and icon support
- ✅ Counts videos and accounts
- ✅ Prevents deleting default collection

### 📊 Analytics

```
GET /api/analytics/overview                # Metrics cards (7/30/90 days)
GET /api/analytics/views-over-time         # Line chart data
GET /api/analytics/most-viral              # Top videos by engagement
GET /api/analytics/virality-analysis       # Distribution chart
GET /api/analytics/duration-analysis       # Duration vs views
GET /api/analytics/metrics-breakdown       # Daily/weekly averages
GET /api/analytics/video-stats             # Performance table
```

**Analytics Features:**
- ✅ Engagement rate calculations
- ✅ Performance multipliers
- ✅ Virality distribution (1x, 5x, 10x, etc.)
- ✅ Duration analysis
- ✅ Daily and weekly averages

### 🔍 Search & Discovery

```
POST /api/search/hashtag       # Search by hashtag
POST /api/search/term          # Search by keyword
GET  /api/trending/audio       # Trending audio by country
GET  /api/stats                # Overall platform stats
```

### ✅ Health Check

```
GET  /                         # API health check
GET  /docs                     # Swagger documentation
```

---

## 🤖 Scrapers

### 1. TikTok Scraper (`scrapers/tiktok_scraper.py`)

**Capabilities:**
- ✅ Search by hashtag
- ✅ Search by keyword
- ✅ Get trending videos
- ✅ Fetch video details
- ✅ Handles rate limiting
- ✅ Auto-captcha solving

**Data Extracted:**
- Video ID, URL, thumbnail
- Caption and hashtags
- Author (username, nickname, avatar)
- Stats (views, likes, comments, shares)
- Music/audio information
- Duration and posted date

### 2. URL Scraper (`scrapers/url_scraper.py`)

**Capabilities:**
- ✅ Scrape single video URLs
- ✅ Scrape profile URLs (all videos)
- ✅ Detect URL type automatically
- ✅ Extract all metrics
- ✅ Handle TikTok short links (vm.tiktok.com)

**Supported Formats:**
```
https://www.tiktok.com/@username/video/123456
https://vm.tiktok.com/abc123
https://www.tiktok.com/@username  (profile)
```

### 3. YouTube Scraper (`scrapers/youtube_scraper.py`)

**Capabilities:**
- ✅ Search by hashtag
- ✅ Search by keyword
- ✅ No API key required
- ✅ Extract video metadata

### 4. Trending Audio Scraper (`scrapers/trending_audio_scraper.py`)

**Capabilities:**
- ✅ Country-specific trending sounds
- ✅ 10+ countries supported
- ✅ Rank and total video counts
- ✅ 1-hour cache

---

## 🔄 Data Flow

### Adding a Video

```
1. User pastes TikTok URL → Frontend
                ↓
2. POST /api/scrape/urls → Backend
                ↓
3. URL Scraper extracts data
                ↓
4. Save to videos table
                ↓
5. Create/update account (auto)
                ↓
6. Add to default collection (auto)
                ↓
7. Refresh account stats (auto)
                ↓
8. Return to frontend
```

### Analytics Query

```
1. GET /api/analytics/overview
                ↓
2. Query videos from last 7 days
                ↓
3. Calculate aggregates
   - Total views, likes, comments
   - Engagement rate
   - Performance metrics
                ↓
4. Return JSON response
                ↓
5. Frontend renders charts
```

---

## 🎨 Logical Features

### Auto-Account Creation

When a video is scraped:
1. Check if account exists (username + platform)
2. If exists: Update avatar, nickname, last_scraped
3. If not: Create new account record
4. Aggregate all videos from that account
5. Update total_videos, total_views, total_likes

### Default Collection

- Auto-creates on first video scrape
- All new videos added automatically
- Cannot be deleted
- Acts as "All Videos" view

### Collection Counts

- Auto-updated when videos added/removed
- Counts both videos and accounts
- Efficient queries with indexes

### Performance Indicators

Analytics calculate:
- **Engagement Rate**: (likes + comments + shares) / views
- **Performance Multiplier**: video_views / average_views
- **Virality Category**: Below 1x, 1x-5x, 5x-10x, etc.

---

## ⚡ Performance Optimizations

### Database Indexes

```sql
-- Videos table
CREATE INDEX idx_platform ON videos(platform);
CREATE INDEX idx_author_username ON videos(author_username);
CREATE INDEX idx_scraped_at ON videos(scraped_at);
CREATE INDEX idx_platform_scraped ON videos(platform, scraped_at);

-- Accounts table
CREATE UNIQUE INDEX idx_username_platform ON accounts(username, platform);

-- Collections relationships
CREATE INDEX idx_video_collection ON video_collections(video_id, collection_id);
CREATE INDEX idx_collection_videos ON video_collections(collection_id, added_at);
```

### Query Optimizations

- Pagination on all list endpoints
- Composite indexes for common queries
- JSON fields for arrays (hashtags, mentions)
- BigInt for large numbers (views, likes)
- Aggregated stats cached in account records

### Async Operations

- Concurrent video scraping
- Non-blocking database queries
- Parallel API requests

---

## 🔒 Error Handling

### Video Scraping

```python
try:
    video_data = await scraper.scrape_url(url)
    # Save to database
except Exception as e:
    errors.append({"url": url, "error": str(e)})
    # Continue with other URLs
```

**Handles:**
- ✅ Invalid URLs
- ✅ Deleted videos
- ✅ Private videos
- ✅ Rate limiting
- ✅ Network errors

### Database Operations

```python
try:
    db.add(video)
    db.commit()
except IntegrityError:
    db.rollback()
    # Update existing record instead
```

**Handles:**
- ✅ Duplicate entries
- ✅ Foreign key violations
- ✅ Transaction rollbacks

---

## 📝 Data Validation

### Pydantic Models

All API requests/responses use Pydantic:

```python
class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = '#8B5CF6'
    icon: Optional[str] = 'folder'

class VideoResponse(BaseModel):
    id: str
    platform: str
    views: int
    likes: int
    # ... etc
```

**Benefits:**
- ✅ Automatic validation
- ✅ Type checking
- ✅ OpenAPI schema generation
- ✅ Clear documentation

---

## 🚀 Running the Backend

### Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright
python -m playwright install

# Configure environment
cp .env.example .env
# Edit DATABASE_URL in .env
```

### Start Server

```bash
python main.py
```

Server runs on: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

---

## 📋 Dependencies

```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
TikTokApi==6.2.0
playwright==1.40.0
youtube-search-python==1.6.6
httpx==0.25.2
python-dotenv==1.0.0
pydantic==2.5.2
```

---

## 🔮 Future Enhancements

### Ready to Implement

1. **User Authentication** (Supabase Auth)
   - Add user_id to all tables
   - Enable Row Level Security
   - User-specific collections

2. **Scheduled Scraping** (Celery/Edge Functions)
   - Auto-refresh tracked accounts
   - Daily trending audio updates
   - Email digests

3. **Real-time Updates** (Supabase Realtime)
   - Live metric updates
   - New video notifications
   - Dashboard auto-refresh

4. **Advanced Analytics**
   - Best posting times
   - Content recommendations
   - Competitor analysis
   - Growth predictions

5. **Export Features**
   - CSV export
   - PDF reports
   - API webhooks

---

## 📊 Current Status

### ✅ Fully Implemented

- [x] Complete database schema
- [x] All scrapers working
- [x] Collections management
- [x] Account tracking
- [x] Analytics endpoints
- [x] Error handling
- [x] Async operations
- [x] Supabase-ready
- [x] API documentation
- [x] Performance optimized

### 📈 Production Ready

- Database schema is stable
- All endpoints tested and working
- Error handling comprehensive
- Performance optimized
- Documentation complete
- Ready for Supabase migration

---

## 🎯 Key Differentiators

1. **Smart Auto-Creation**
   - Accounts auto-created from videos
   - Default collection auto-created
   - Stats auto-aggregated

2. **Flexible Collections**
   - Organize by campaign, client, niche
   - Color coding and icons
   - Count tracking

3. **Comprehensive Analytics**
   - Engagement rates
   - Performance multipliers
   - Virality distribution
   - Duration analysis

4. **Professional SaaS Architecture**
   - Clean API design
   - Proper error handling
   - Efficient queries
   - Scalable structure

---

## 📞 API Documentation

Full interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

**Your backend is complete, tested, and ready for Supabase!** 🎉

Just update your `DATABASE_URL` to point to Supabase and you're production-ready.
