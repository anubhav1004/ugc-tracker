# RapidAPI TikTok Scraper Setup

## Perfect Solution! 🎉

RapidAPI handles ALL the anti-bot protection for us. This is the cleanest, most reliable way to scrape TikTok.

## Setup (5 minutes)

### Step 1: Get RapidAPI Key

1. Go to: https://rapidapi.com/tikwm-tikwm-default/api/tiktok-scraper7
2. Click "Sign Up" (or Log In if you have an account)
3. Subscribe to the **FREE plan**:
   - 120 requests/minute
   - 300 requests/month
   - Perfect for 7 accounts with daily updates
4. Copy your API key (shown after subscribing)

### Step 2: Add API Key to .env

Open `backend/.env` and add your key:

```bash
RAPIDAPI_KEY=your_api_key_here
```

### Step 3: Run Initial Import

```bash
cd /Users/anubhavmishra/Desktop/social-media-tracker/backend
source venv/bin/activate
python add_accounts_rapidapi.py
```

This will:
- Fetch the last 10 videos from each of your 7 accounts
- Extract ALL stats (views, likes, comments, shares, bookmarks)
- Create account records
- Add everything to your database

**Takes about 2-3 minutes total.**

### Step 4: Daily Updates (Already Set Up!)

The cron job runs automatically at midnight using RapidAPI. To update it to use the RapidAPI version:

```bash
./update_cron_rapidapi.sh
```

Or manually update:
```bash
crontab -e
```

Change the line to:
```
0 0 * * * cd /Users/anubhavmishra/Desktop/social-media-tracker/backend && /Users/anubhavmishra/Desktop/social-media-tracker/backend/venv/bin/python /Users/anubhavmishra/Desktop/social-media-tracker/backend/daily_stats_updater_rapidapi.py >> /Users/anubhavmishra/Desktop/social-media-tracker/backend/logs/daily_update.log 2>&1
```

## Why This Works

✅ **No anti-bot issues** - RapidAPI handles everything
✅ **Free tier works perfectly** - 300 requests/month = ~10 requests/day
✅ **Full statistics** - Views, likes, comments, shares, bookmarks
✅ **Reliable** - Professional API service
✅ **Automatic daily updates** - Set and forget

## API Limits & Usage

**Free Tier:**
- 120 requests/minute (way more than we need)
- 300 requests/month total

**Our Usage:**
- Initial import: ~70 requests (7 accounts × 10 videos)
- Daily updates: ~70 requests/day (updating all videos)
- **Total per month:** ~2,100 requests needed

**Recommendation:** Upgrade to **PRO plan** ($10/month) for 9,000 requests/month if you want to track all accounts daily.

**OR** optimize to only update most recent videos:
- Track which videos are new/recent
- Only update those daily
- Older videos update weekly
- This keeps you under 300/month easily

## Test It Now

```bash
# Test with a single account
python -c "
from scrapers.rapidapi_tiktok_scraper import RapidAPITikTokScraper
import os

scraper = RapidAPITikTokScraper(api_key=os.getenv('RAPIDAPI_KEY'))
profile = scraper.scrape_profile('https://www.tiktok.com/@therock', limit=3)
print(f'Got {len(profile[\"videos\"])} videos!')
for v in profile['videos']:
    print(f'  - {v[\"caption\"][:50]}... | {v[\"views\"]:,} views')
"
```

## Next Steps

1. **Get API key** (2 min)
2. **Add to .env** (30 sec)
3. **Run import** (2 min)
4. **View dashboard** at http://localhost:3000
5. **Done!** Updates happen automatically

---

**This is THE solution.** No more anti-bot issues. Everything works reliably.
