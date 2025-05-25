#!/bin/bash

# Stop the bot

echo "Stopping Telegram bot..."

# Check if PID file exists
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ Bot stopped (PID: $PID)"
        rm bot.pid
    else
        echo "⚠️  Bot process not found (PID: $PID)"
        echo "Cleaning up stale PID file..."
        rm bot.pid
    fi
else
    echo "No bot.pid file found. Checking for running processes..."
    # Try to find and kill any running bot process
    PIDS=$(pgrep -f "python offer_monitor_bot.py")
    if [ ! -z "$PIDS" ]; then
        echo "Found bot process(es): $PIDS"
        kill $PIDS
        echo "✅ Bot process(es) stopped"
    else
        echo "❌ No bot process found running"
    fi
fi

# Clean up any stale session locks
if [ -f sessions/*.session-journal ]; then
    rm -f sessions/*.session-journal
    echo "🧹 Cleaned up session lock files"
fi

echo "Done." 