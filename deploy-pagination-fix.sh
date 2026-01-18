#!/bin/bash

echo "🚀 Deploying Pagination Fix to Production"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "backend/scrapers/rapidapi_tiktok_scraper.py" ]; then
    echo "❌ Error: Run this script from the project root directory"
    exit 1
fi

echo "📦 Files to deploy:"
echo "  1. backend/scrapers/rapidapi_tiktok_scraper.py (pagination support)"
echo "  2. backend/scrapers/url_scraper.py (uses pagination)"
echo ""

# Commit changes
echo "📝 Committing changes..."
git add backend/scrapers/rapidapi_tiktok_scraper.py backend/scrapers/url_scraper.py
git commit -m "Fix: Add pagination to fetch all TikTok videos from profiles

- Added get_all_user_posts() with cursor-based pagination
- Added scrape_profile_all() to fetch unlimited videos
- Updated URLScraper to use pagination
- Now fetches ALL videos instead of just 33-35

Tested locally with karissa.curious (60 videos), max.curious1 (77 videos),
mari.curious (79 videos) - all videos successfully scraped.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

if [ $? -ne 0 ]; then
    echo "⚠️  Commit may have failed (changes might already be committed)"
fi

echo ""
echo "🔄 Syncing with remote..."
git pull --rebase origin main

if [ $? -ne 0 ]; then
    echo "⚠️  Pull failed - you may need to resolve conflicts manually"
    echo ""
    echo "To fix conflicts:"
    echo "  1. git status (see conflicting files)"
    echo "  2. Edit files to resolve conflicts"
    echo "  3. git add <resolved-files>"
    echo "  4. git rebase --continue"
    echo "  5. Run this script again"
    exit 1
fi

echo ""
echo "⬆️  Pushing to remote..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Pagination fix deployed to GitHub"
    echo ""
    echo "📊 What happens now:"
    echo "  • Railway/Vercel will auto-deploy the backend"
    echo "  • Production will now scrape ALL videos from profiles"
    echo "  • No more 33-video limit!"
    echo ""
    echo "🧪 Test in production:"
    echo "  1. Go to your production app"
    echo "  2. Add account: https://www.tiktok.com/@karissa.curious"
    echo "  3. Should scrape all 60 videos (not just 33)"
    echo ""
else
    echo ""
    echo "⚠️  Push failed. Manual deployment options:"
    echo ""
    echo "Option 1: Copy files to production server"
    echo "  - backend/scrapers/rapidapi_tiktok_scraper.py"
    echo "  - backend/scrapers/url_scraper.py"
    echo ""
    echo "Option 2: Use Railway CLI"
    echo "  railway up"
    echo ""
    echo "Option 3: Force push (use with caution)"
    echo "  git push -f origin main"
    echo ""
fi
