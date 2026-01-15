#!/bin/bash

# Update cron job to use RapidAPI version of daily updater

echo "🔧 Updating cron job to use RapidAPI..."

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/daily_stats_updater_rapidapi.py"
LOG_PATH="$PROJECT_DIR/logs/daily_update.log"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Remove old cron jobs
crontab -l 2>/dev/null | grep -v "daily_stats_updater" | crontab -

# Add new cron job with RapidAPI version
CRON_CMD="0 0 * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $LOG_PATH 2>&1"
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "✅ Cron job updated successfully!"
echo ""
echo "📋 Using: daily_stats_updater_rapidapi.py"
echo "   (No more anti-bot issues!)"
echo ""
echo "🔍 Verify:"
echo "   crontab -l"
