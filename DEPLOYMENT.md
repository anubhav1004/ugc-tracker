# UGC Tracker - Production Deployment Guide

This guide walks you through deploying UGC Tracker with a hybrid architecture:
- **Frontend**: Vercel (optimized for React)
- **Backend**: Railway or Render (optimized for FastAPI)

---

## Prerequisites

- [x] GitHub repository created: https://github.com/anubhav1004/ugc-tracker
- [ ] Vercel account (sign up at https://vercel.com)
- [ ] Railway account (sign up at https://railway.app) **OR** Render account (https://render.com)
- [ ] Supabase account for PostgreSQL database (https://supabase.com)
- [ ] RapidAPI key for TikTok/Instagram scraping

---

## Part 1: Deploy Backend (Railway - Recommended)

### Step 1: Create Railway Project

1. Go to https://railway.app and sign in with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose repository: `anubhav1004/ugc-tracker`
5. Click **"Deploy Now"**

### Step 2: Configure Backend Service

1. After deployment starts, click on your service
2. Go to **"Settings"** tab
3. Scroll to **"Root Directory"**
4. Enter: `backend`
5. Click **"Update"**

### Step 3: Generate Public URL

1. In Settings, scroll to **"Networking"**
2. Click **"Generate Domain"**
3. Copy your backend URL (e.g., `https://ugc-tracker-production.up.railway.app`)
4. **Save this URL** - you'll need it for frontend

### Step 4: Add Environment Variables

1. Go to **"Variables"** tab
2. Click **"Add Variable"** and add each of these:

```
DATABASE_URL=postgresql://user:password@host:5432/database
RAPIDAPI_KEY=your_rapidapi_key_here
PORT=8000
HOST=0.0.0.0
```

3. Click **"Deploy"** to restart with new variables

---

## Part 2: Set Up Database (Supabase)

### Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click **"New Project"**
3. Enter project details:
   - **Name**: ugc-tracker
   - **Database Password**: (create a strong password)
   - **Region**: Choose closest to you
4. Click **"Create new project"**
5. Wait 2-3 minutes for provisioning

### Step 2: Get Connection String

1. In your Supabase project, go to **"Settings"** → **"Database"**
2. Scroll to **"Connection string"**
3. Select **"URI"** tab
4. Copy the connection string
5. Replace `[YOUR-PASSWORD]` with your actual database password

### Step 3: Update Railway Environment

1. Go back to Railway dashboard
2. Select your backend service
3. Go to **"Variables"** tab
4. Edit `DATABASE_URL` variable
5. Paste your Supabase connection string
6. Service will automatically redeploy

### Step 4: Verify Backend is Running

1. Open your Railway backend URL in browser
2. You should see: `{"message": "Social Media Tracker API"}`
3. Test API docs: `https://your-backend-url.com/docs`

---

## Part 3: Deploy Frontend (Vercel)

### Step 1: Import Project to Vercel

1. Go to https://vercel.com and sign in with GitHub
2. Click **"Add New"** → **"Project"**
3. Find and select: `anubhav1004/ugc-tracker`
4. Click **"Import"**

### Step 2: Configure Build Settings

Vercel should auto-detect these settings:

- **Framework Preset**: Create React App
- **Root Directory**: `frontend` ← **IMPORTANT: Click "Edit" and enter this**
- **Build Command**: `npm run build`
- **Output Directory**: `build`
- **Install Command**: `npm install`

### Step 3: Add Environment Variable

1. Before deploying, click **"Environment Variables"**
2. Add variable:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: Your Railway backend URL (e.g., `https://ugc-tracker-production.up.railway.app`)
   - **DO NOT** add trailing slash
3. Click **"Add"**

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. Once complete, click **"Visit"** to see your live app
4. Copy your Vercel URL (e.g., `https://ugc-tracker.vercel.app`)

---

## Part 4: Test Your Deployment

### Test Checklist

1. **Frontend loads**: Visit your Vercel URL
2. **Dark mode works**: Toggle theme in sidebar
3. **Analytics load**: Check Overview dashboard shows data or empty state
4. **Add Account works**: Try adding a TikTok or Instagram profile
5. **API connection**: Open browser console, check for CORS or API errors

### Common Issues

**Issue**: CORS errors in browser console
**Fix**: Backend CORS is already configured for `*`. Check that `REACT_APP_API_URL` is correct.

**Issue**: "Failed to fetch" errors
**Fix**: Verify Railway backend is running and URL is correct (no trailing slash).

**Issue**: Database connection errors in Railway logs
**Fix**: Check Supabase connection string is correct and includes password.

---

## Part 5: Configure CORS (If Needed)

If you see CORS errors, update backend CORS settings:

1. In Railway, go to **"Variables"**
2. Add variable:
   - **Name**: `FRONTEND_URL`
   - **Value**: Your Vercel URL (e.g., `https://ugc-tracker.vercel.app`)
3. Service will redeploy

---

## Alternative: Deploy Backend to Render

If you prefer Render over Railway:

### Step 1: Create Web Service

1. Go to https://render.com and sign in
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository: `anubhav1004/ugc-tracker`
4. Click **"Connect"**

### Step 2: Configure Service

- **Name**: ugc-tracker-backend
- **Region**: Oregon (or closest to you)
- **Root Directory**: `backend`
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables

Click **"Advanced"** and add:

```
DATABASE_URL=your_supabase_connection_string
RAPIDAPI_KEY=your_rapidapi_key
PORT=8000
HOST=0.0.0.0
```

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment
3. Copy your Render URL
4. Use this URL as `REACT_APP_API_URL` in Vercel

---

## Environment Variables Summary

### Backend (Railway/Render)
```
DATABASE_URL=postgresql://user:password@host:5432/database
RAPIDAPI_KEY=your_rapidapi_key_here
PORT=8000
HOST=0.0.0.0
```

### Frontend (Vercel)
```
REACT_APP_API_URL=https://your-backend-url.com
```

---

## Next Steps

1. **Custom Domain** (Optional): Add custom domain in Vercel settings
2. **Monitoring**: Check Railway/Render logs for errors
3. **Analytics**: Monitor Vercel analytics for traffic
4. **Scaling**: Railway/Render auto-scale with traffic

---

## Support

- **Frontend Issues**: Check Vercel deployment logs
- **Backend Issues**: Check Railway/Render logs
- **Database Issues**: Check Supabase logs
- **API Issues**: Test endpoints at `/docs` on your backend URL

---

## Costs

- **Vercel**: Free tier (sufficient for small projects)
- **Railway**: $5/month after free trial ($5 credit included)
- **Render**: Free tier available (spins down after inactivity)
- **Supabase**: Free tier (500MB database, 2GB bandwidth)

---

**Deployment complete!** 🚀

Your UGC Tracker is now live:
- Frontend: https://your-vercel-url.vercel.app
- Backend: https://your-railway-url.up.railway.app
- Database: Hosted on Supabase
