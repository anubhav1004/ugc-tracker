#!/bin/bash

# Setup script for daily stats updater cron job
# Runs daily_stats_updater.py every day at midnight

echo "🔧 Setting up daily cron job for TikTok stats updater..."

# Get the absolute path to the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/daily_stats_updater.py"
LOG_PATH="$PROJECT_DIR/logs/daily_update.log"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Create the cron job command
CRON_CMD="0 0 * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $LOG_PATH 2>&1"

# Check if cron job already exists
crontab -l 2>/dev/null | grep -q "daily_stats_updater.py"

if [ $? -eq 0 ]; then
    echo "⚠️  Cron job already exists. Updating..."
    # Remove old cron job
    crontab -l 2>/dev/null | grep -v "daily_stats_updater.py" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "📋 Job details:"
echo "   Schedule: Every day at midnight (12:00 AM)"
echo "   Script: $SCRIPT_PATH"
echo "   Logs: $LOG_PATH"
echo ""
echo "🔍 To view your cron jobs:"
echo "   crontab -l"
echo ""
echo "📝 To view update logs:"
echo "   tail -f $LOG_PATH"
echo ""
echo "❌ To remove the cron job:"
echo "   crontab -e"
echo "   (then delete the line containing 'daily_stats_updater.py')"
