# UGC Tracker

A comprehensive UGC (User Generated Content) analytics platform for tracking TikTok and Instagram content creators and analyzing their performance metrics in real-time.

![Platform](https://img.shields.io/badge/Platform-TikTok%20%7C%20Instagram-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 📊 Analytics Dashboard
- **Real-time metrics**: Track views, engagement, likes, comments, and shares
- **Platform filtering**: Filter data by TikTok, Instagram, or view all platforms
- **Metric type filters**: View total, organic, or ads metrics separately
- **Performance tracking**: Monitor cumulative views over time
- **Virality analysis**: Track content performance multipliers
- **Duration analysis**: Understand which video lengths perform best

### 📹 Video Management
- **All Videos view**: Browse and filter all tracked videos
- **Creator filtering**: Filter videos by specific creators
- **Date range filtering**: Analyze performance within custom date ranges
- **Spark Ad labeling**: Mark and track promoted content
- **Video statistics**: Detailed metrics for each video

### 👥 Account Management
- **Add accounts**: Track TikTok and Instagram profiles via URL
- **Bulk import**: Add multiple accounts at once
- **Profile scraping**: Automatically fetch all videos from a profile
- **Creator profiles**: View aggregated stats per creator

### 📁 Collections
- **Organize content**: Create custom collections to group videos
- **Color coding**: Visual organization with customizable colors
- **Default collection**: Automatically save new videos

### 🎨 UI/UX
- **Dark mode**: Full dark theme support
- **Responsive design**: Works on desktop and mobile
- **Real-time updates**: Data refreshes automatically
- **Fixed sidebar navigation**: Easy access to all features

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (Supabase) / SQLite fallback
- **ORM**: SQLAlchemy
- **API Integration**: RapidAPI for Instagram & TikTok data
- **Async**: asyncio for concurrent scraping

### Frontend
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React
- **Routing**: React Router v6
- **HTTP Client**: Axios

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 16 or higher
- PostgreSQL 14+ (or use SQLite for development)
- RapidAPI key for Instagram & TikTok APIs

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ugc-tracker.git
cd ugc-tracker
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOL
DATABASE_URL=your_postgresql_url
RAPIDAPI_KEY=your_rapidapi_key
PORT=8000
HOST=0.0.0.0
EOL
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
```

## 🏃 Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
python main.py
```

Backend runs on: **http://localhost:8000**
API docs: **http://localhost:8000/docs**

### Start Frontend (Terminal 2)

```bash
cd frontend
npm start
```

Frontend runs on: **http://localhost:3000**

## 📡 API Endpoints

### Analytics
- `GET /api/analytics/overview?days=7&metric_type=total&platform=tiktok`
- `GET /api/analytics/views-over-time?days=7&metric_type=total&platform=instagram`
- `GET /api/analytics/most-viral?limit=3&metric_type=total&platform=tiktok`
- `GET /api/analytics/video-stats?limit=20&metric_type=total`

### Videos
- `GET /api/videos?creator=username&platform=tiktok&limit=50`
- `GET /api/videos/{video_id}`
- `PATCH /api/videos/{video_id}/spark-ad?is_spark_ad=true`

### Accounts
- `GET /api/creators`
- `POST /api/scrape/urls` - Add accounts by URL

### Collections
- `GET /api/collections`
- `POST /api/collections`
- `DELETE /api/collections/{id}`

## 🎯 Usage Guide

### Adding Accounts

1. Navigate to **Add Accounts** page
2. Paste TikTok or Instagram profile URL
3. Click **Add to Dashboard**
4. Videos will be automatically scraped and added

### Viewing Analytics

1. Go to **Overview** (Analytics Dashboard)
2. Use platform filters: All / TikTok / Instagram
3. Select metric type: Total / Organic / Ads
4. Change date range for time-based analysis

### Filtering Videos

1. Navigate to **All Videos**
2. Use the filter panel:
   - Filter by creator
   - Set date range
   - Filter by video type
3. Click **Apply Filters**

### Creating Collections

1. Click **Collections** in sidebar
2. Click **New Collection**
3. Enter name and choose color
4. Organize videos into collections

## 🗄️ Database Schema

### Videos Table
```sql
- id (String, Primary Key)
- platform (String: 'tiktok' | 'instagram')
- url (String)
- thumbnail (String)
- caption (Text)
- author_username (String)
- author_nickname (String)
- views (Integer)
- likes (Integer)
- comments (Integer)
- shares (Integer)
- bookmarks (Integer)
- duration (Integer, seconds)
- is_spark_ad (Boolean)
- posted_at (DateTime)
- scraped_at (DateTime)
```

### Collections Table
```sql
- id (UUID, Primary Key)
- name (String)
- description (Text)
- color (String)
- is_default (Boolean)
```

## ⚙️ Configuration

### Environment Variables

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
RAPIDAPI_KEY=your_rapidapi_key_here
PORT=8000
HOST=0.0.0.0
```

**Frontend (.env.local)**
```env
REACT_APP_API_URL=http://localhost:8000
```

## 🚢 Deployment

### Deploying to Vercel

**Frontend Deployment:**
1. Push code to GitHub
2. Import project in Vercel
3. Set root directory to `frontend`
4. Add environment variable: `REACT_APP_API_URL=your_backend_url`
5. Deploy

**Backend Deployment (Railway/Render):**
1. Connect GitHub repository
2. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Add environment variables from `.env`
4. Deploy

### Database (Supabase)
1. Create new project on Supabase
2. Copy PostgreSQL connection string
3. Update `DATABASE_URL` in backend environment

## 🔧 Troubleshooting

### Backend Issues

**Import Error: No module named 'scrapers'**
- Ensure `scrapers/__init__.py` exists
- Run: `touch backend/scrapers/__init__.py`

**Database Connection Failed**
- Check DATABASE_URL is correct
- App will fallback to SQLite automatically

**RapidAPI Errors**
- Verify RAPIDAPI_KEY is set correctly
- Check API quota hasn't been exceeded

### Frontend Issues

**CORS Errors**
- Ensure backend CORS is configured
- Verify `REACT_APP_API_URL` matches backend

**Filters Not Working**
- Hard refresh: Cmd+Shift+R (Mac) / Ctrl+Shift+R (Windows)
- Clear browser cache

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 💡 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Recharts](https://recharts.org/)
- [RapidAPI](https://rapidapi.com/)

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ for content creators and marketers**
