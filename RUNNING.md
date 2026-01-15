# 🚀 Social Media Tracker - NOW RUNNING!

## ✅ Application Status

### Backend API
- **URL**: http://localhost:8000
- **Status**: ✅ Running
- **API Docs**: http://localhost:8000/docs
- **Health**: {"status":"ok","message":"Social Media Tracker API is running"}

### Frontend
- **URL**: http://localhost:3000
- **Status**: ✅ Running
- **Browser**: Should be open automatically

### Database
- **Type**: PostgreSQL
- **Name**: social_media_tracker
- **Status**: ✅ Connected

## 🎯 How to Use

### 1. Dashboard (Home Page)
- View overall statistics
- See platform breakdowns
- Check trending videos
- **URL**: http://localhost:3000/

### 2. Search for Videos
- Navigate to: http://localhost:3000/search
- Choose: Hashtag or Term search
- Select platform: TikTok or YouTube
- Enter query and click Search

**Example Searches:**
- Hashtag: `travel` on TikTok
- Term: `python tutorial` on YouTube
- Hashtag: `coding` on YouTube

### 3. Trending Audio by Country
- Navigate to: http://localhost:3000/trending
- Select country (US, UK, India, etc.)
- View top 50 trending sounds
- Click play button to listen

## 📊 API Examples

### Test with curl:

```bash
# Health check
curl http://localhost:8000/

# Get statistics
curl http://localhost:8000/api/stats

# Search hashtag on TikTok
curl -X POST http://localhost:8000/api/search/hashtag \
  -H "Content-Type: application/json" \
  -d '{"query": "travel", "platform": "tiktok", "limit": 10}'

# Get trending audio for US
curl "http://localhost:8000/api/trending/audio?country=US&limit=20"

# Search term on YouTube
curl -X POST http://localhost:8000/api/search/term \
  -H "Content-Type: application/json" \
  -d '{"query": "python", "platform": "youtube", "limit": 10}'
```

## 🖥️ Process Information

### Backend Process
- Working Directory: `/Users/anubhavmishra/Desktop/social-media-tracker/backend`
- Log File: `backend.log`
- Command: `python main.py`

### Frontend Process
- Working Directory: `/Users/anubhavmishra/Desktop/social-media-tracker/frontend`
- Log File: `frontend.log`
- Command: `npm start`

## 🛑 Stop the Application

```bash
# Stop all processes
cd /Users/anubhavmishra/Desktop/social-media-tracker

# Stop backend
lsof -ti:8000 | xargs kill

# Stop frontend
lsof -ti:3000 | xargs kill
```

## 🔄 Restart the Application

```bash
cd /Users/anubhavmishra/Desktop/social-media-tracker

# Terminal 1 - Backend
cd backend
source venv/bin/activate
export DATABASE_URL="postgresql://anubhavmishra@localhost:5432/social_media_tracker"
python main.py

# Terminal 2 - Frontend (new terminal)
cd frontend
npm start
```

## 📝 Notes

- First searches may take 10-30 seconds as scrapers initialize
- TikTok scraping works without authentication but may be rate-limited
- For better results, add TikTok `ms_token` to `backend/.env`
- YouTube scraping is faster and doesn't require authentication
- Trending audio data is cached for 1 hour

## 🔍 Troubleshooting

### Backend not responding
- Check: `tail -f backend/backend.log`
- Verify PostgreSQL is running: `brew services list | grep postgresql`

### Frontend not loading
- Check: `tail -f frontend/frontend.log`
- Clear browser cache
- Try incognito mode

### No search results
- Backend might be rate-limited
- Try a different search term
- Check backend logs for errors

## 🎉 Ready to Use!

Your Social Media Tracker is fully operational. Start by:
1. Going to http://localhost:3000
2. Clicking on "Search" in the navigation
3. Try searching for a hashtag like "travel" on TikTok
4. Check out the Trending Audio page for different countries

Enjoy tracking social media! 🚀
