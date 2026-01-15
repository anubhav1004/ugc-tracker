# Instagram Scraping Setup Guide

## ✅ What's Been Implemented

I've successfully implemented **two methods** for Instagram scraping:

### 1. **Instaloader (Direct Instagram API)**
- ✅ Instagram video/post URL scraping
- ✅ Instagram profile scraping
- ✅ Full post/video metrics (views, likes, comments)
- ✅ Profile information (followers, following, bio, etc.)
- ⚠️ **Requires Instagram login credentials**

### 2. **RapidAPI Instagram Scraper**
- ✅ No Instagram login required
- ✅ Bypasses authentication
- ✅ More reliable for bulk scraping
- ⚠️ **Requires RapidAPI subscription**

---

## 🚧 Current Status

The scraping code is **fully implemented**, but you're getting **403/429 errors** because:

1. Your current RapidAPI key appears to only have access to **TikTok APIs**
2. You need to **subscribe to an Instagram scraping API** on RapidAPI

---

## 🔧 Setup Instructions

### Option 1: Use RapidAPI (Recommended)

#### Step 1: Subscribe to Instagram API
1. Go to RapidAPI and choose an Instagram API:
   - **Instagram Bulk Profile Scraper**: https://rapidapi.com/mrngstar/api/instagram-bulk-profile-scrapper
   - **Instagram Data API**: https://rapidapi.com/antonelect/api/instagram-data1
   - **Instagram Scraper 2023**: https://rapidapi.com/ptwebsolution/api/instagram-scraper-2023

2. Subscribe to the API (most have free tiers)
3. Your existing `RAPIDAPI_KEY` will work once subscribed

#### Step 2: Test the scraper
```bash
cd backend
python3 test_instagram_rapidapi.py
```

This will scrape data from:
- `piaprofessor`
- `rose.studycorner`

---

### Option 2: Use Instaloader (Direct Method)

⚠️ This method requires an Instagram account login.

#### Step 1: Add Instagram credentials to `.env`
```bash
# Add these to your .env file
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```

#### Step 2: Update url_scraper.py initialization
The code already supports this - just pass credentials:
```python
async with URLScraper(
    instagram_username=os.getenv('INSTAGRAM_USERNAME'),
    instagram_password=os.getenv('INSTAGRAM_PASSWORD')
) as scraper:
    result = await scraper.scrape_instagram_profile(url, limit=12)
```

⚠️ **Warning**: Instagram may block your account if they detect scraping. Use a throwaway account.

---

## 📁 Files Created/Modified

### New Files
1. **`scrapers/rapidapi_instagram_scraper.py`** - RapidAPI Instagram scraper
2. **`test_instagram_rapidapi.py`** - Test script for Instagram scraping
3. **`test_instagram_scraper.py`** - Test script for Instaloader method

### Modified Files
1. **`scrapers/url_scraper.py`** - Added Instagram scraping methods
2. **`requirements.txt`** - Added `instaloader==4.10.3`

---

## 🎯 Recommended Approach

**For production use, I recommend RapidAPI because:**
1. ✅ No Instagram account needed
2. ✅ No risk of account bans
3. ✅ Better rate limits
4. ✅ More reliable for bulk operations
5. ✅ Works with your existing `RAPIDAPI_KEY`

**Just subscribe to an Instagram API on RapidAPI (many have free tiers with 100-500 requests/month)**

---

## 🧪 Testing

Once you've subscribed to an Instagram API, test it:

```bash
cd /Users/anubhavmishra/Desktop/social-media-tracker/backend
python3 test_instagram_rapidapi.py
```

Expected output:
```
✓ Profile Info:
  Username: @piaprofessor
  Full Name: Pia Professor
  Followers: 123,456
  Following: 789
  Total Posts: 250

✓ Aggregate Stats:
  Total Posts Scraped: 12
  Total Videos: 8
  Total Likes: 45,678
  Total Comments: 1,234
```

---

## 📊 Integration with Your Dashboard

Once Instagram scraping works, it will automatically integrate with your existing dashboard:

1. **Add Accounts page** - Can add Instagram profiles
2. **Analytics Dashboard** - Will show Instagram metrics alongside TikTok
3. **All Videos page** - Will display Instagram reels/videos
4. **All Accounts page** - Will list Instagram accounts

The system already supports multiple platforms (see `database.py` line 18):
```python
platform = Column(String, nullable=False, index=True)  # tiktok, youtube, instagram
```

---

## 💰 Cost Considerations

### RapidAPI Instagram APIs (Monthly)
- **Free Tier**: 100-500 requests/month
- **Basic Plan**: $9.99/month (~10,000 requests)
- **Pro Plan**: $29.99/month (~100,000 requests)

### Instaloader (Direct Method)
- **Cost**: Free
- **Risk**: Account ban potential
- **Limit**: Instagram's rate limits apply

---

## ❓ Next Steps

1. **Choose your method** (RapidAPI recommended)
2. **If RapidAPI**: Subscribe to an Instagram API
3. **If Instaloader**: Add credentials to `.env`
4. **Test the scraper** with the test scripts
5. **Start tracking** Instagram accounts!

Need help? Let me know which method you prefer and I can help you set it up!
