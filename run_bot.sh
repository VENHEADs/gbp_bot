#!/bin/bash

# Run the bot in background with nohup
echo "Starting Telegram bot in background..."

# Check if bot is already running
if pgrep -f "python offer_monitor_bot.py" > /dev/null; then
    echo "Bot is already running!"
    echo "To stop it, run: ./stop_bot.sh"
    exit 1
fi

# Start the bot with nohup
nohup python offer_monitor_bot.py > bot_console.log 2>&1 &

# Get the PID
PID=$!
echo $PID > bot.pid

echo "✅ Bot started with PID: $PID"
echo "📋 Logs: tail -f bot.log"
echo "📋 Console output: tail -f bot_console.log"
echo "🛑 To stop: ./stop_bot.sh" 