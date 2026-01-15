# Quick Start Guide

## Fastest Way to Get Running

### Step 1: Install PostgreSQL (if not already installed)

```bash
brew install postgresql
brew services start postgresql
```

### Step 2: Create Database

```bash
createdb social_media_tracker
```

### Step 3: Install Dependencies

```bash
cd /Users/anubhavmishra/Desktop/social-media-tracker
chmod +x setup-all.sh
./setup-all.sh
```

This script will:
- Create Python virtual environment
- Install all Python dependencies
- Install Playwright browsers
- Install all Node.js dependencies
- Create .env files

### Step 4: Start the Backend

Open a new terminal:

```bash
cd /Users/anubhavmishra/Desktop/social-media-tracker/backend
source venv/bin/activate
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Start the Frontend

Open another terminal:

```bash
cd /Users/anubhavmishra/Desktop/social-media-tracker/frontend
npm start
```

Browser will automatically open to: http://localhost:3000

## What You Can Do

### 1. Search for Videos
- Go to "Search" page
- Try searching:
  - Hashtag: `travel` on TikTok
  - Term: `python tutorial` on YouTube

### 2. View Trending Audio
- Go to "Trending Audio" page
- Select a country (e.g., US, UK, India)
- See top trending sounds

### 3. Dashboard
- View statistics
- See trending videos

## Troubleshooting

### "Connection refused" error
- Make sure PostgreSQL is running: `brew services list`
- Check database exists: `psql -l | grep social_media_tracker`

### "No module named playwright"
- Activate virtual environment: `source venv/bin/activate`
- Install playwright: `python -m playwright install`

### TikTok scraping returns empty
- Optional: Add TikTok session token to `backend/.env`
- Get from browser cookies (see README for instructions)

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check `REACT_APP_API_URL` in frontend/.env.local

## API Documentation

Once backend is running, visit:
http://localhost:8000/docs

Interactive API documentation with all endpoints.

## Project Structure

```
social-media-tracker/
├── backend/
│   ├── database.py          # Database models
│   ├── main.py              # FastAPI app
│   ├── scrapers/
│   │   ├── tiktok_scraper.py
│   │   ├── youtube_scraper.py
│   │   └── trending_audio_scraper.py
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Dashboard.js
    │   │   ├── HashtagSearch.js
    │   │   ├── TrendingAudio.js
    │   │   └── VideoCard.js
    │   ├── App.js
    │   └── api.js
    └── package.json
```

## Next Steps

1. **Improve TikTok Results**: Add `TIKTOK_MS_TOKEN` to `.env`
2. **Add More Platforms**: Implement Instagram scraper
3. **Background Jobs**: Set up Celery for automated scraping
4. **Caching**: Add Redis for better performance
5. **Deploy**: Use Docker for production deployment

## Support

- Check README.md for detailed documentation
- Review code comments for implementation details
- Open GitHub issue for bugs/questions
