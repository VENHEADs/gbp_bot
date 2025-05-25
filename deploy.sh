#!/bin/bash

# Railway Deployment Script for Telegram Bot
# This script helps prepare and deploy the bot to Railway

set -e

echo "🚀 Railway Deployment Script"
echo "============================"

# Check if we're in the right directory
if [ ! -f "offer_monitor_bot.py" ]; then
    echo "🔴 Error: offer_monitor_bot.py not found. Please run this script from the project root."
    exit 1
fi

# Check if config.ini exists for local session authorization
if [ ! -f "config.ini" ]; then
    echo "🔴 Error: config.ini not found. Please create it from config.example.ini first."
    exit 1
fi

# Step 1: Authorize session locally
echo "📱 Step 1: Authorizing Telegram session locally..."
if [ ! -d ".venv" ]; then
    echo "🔴 Error: Virtual environment not found. Please run 'python3 -m venv .venv' first."
    exit 1
fi

source .venv/bin/activate
python authorize_session.py

# Check if session was created
if [ ! -f "sessions/my_telegram_session.session" ]; then
    echo "🔴 Error: Session authorization failed. Please check your credentials."
    exit 1
fi

echo "✅ Session authorized successfully!"

# Step 2: Commit session file to git (if not already)
echo "📝 Step 2: Adding session file to git..."
git add sessions/
git add authorize_session.py env.example Dockerfile railway.toml
git commit -m "Add Railway deployment files and authorized session" || echo "ℹ️  No changes to commit"

# Step 3: Push to GitHub
echo "📤 Step 3: Pushing to GitHub..."
git push origin main || git push origin master

echo ""
echo "✅ Deployment preparation complete!"
echo ""
echo "🔗 Next steps:"
echo "1. Go to https://railway.app and create a new project"
echo "2. Connect your GitHub repository: https://github.com/VENHEADs/$(basename $(pwd))"
echo "3. Set the following environment variables in Railway:"
echo "   - API_ID"
echo "   - API_HASH" 
echo "   - PHONE_NUMBER"
echo "   - TARGET_GROUP_ID"
echo "   - TARGET_TOPIC_ID"
echo "   - NOTIFY_USER_ID"
echo "   - SESSION_NAME=my_telegram_session"
echo "4. Deploy and monitor the logs!"
echo ""
echo "🎉 Your bot will be running 24/7 on Railway!" 