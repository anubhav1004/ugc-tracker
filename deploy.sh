#!/bin/bash
cd /Users/anubhavmishra/Desktop/social-media-tracker
git add backend/main.py frontend/src/components/AnalyticsDashboard.js
git commit -m "Add date filters, collection analytics, and account management

- Add Last 30 Days and All Time date filter options
- Fix analytics to filter by posted_at instead of scraped_at
- Add collection filtering to all analytics endpoints
- Add account management endpoints for collections
- Increase max days from 90 to 365

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push origin main
