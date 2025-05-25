# Telegram Currency Exchange Bot 💱

An automated Telegram bot that monitors currency exchange groups for RUB/GBP offers and automatically responds to potential trading partners.

## 🚀 Features

- **Real-time Monitoring**: Listens to specific Telegram groups/topics for currency exchange messages
- **Intelligent Parsing**: Analyzes messages to identify ruble buying/selling offers
- **Auto-Response**: Automatically messages users looking to buy rubles with a Russian greeting
- **Fallback Notifications**: Sends alerts to bot owner for non-auto-responded offers
- **Cloud Ready**: Deployable to Railway or any Docker-compatible platform

## 📋 Prerequisites

- Python 3.11+
- Telegram API credentials (api_id and api_hash)
- Access to the Telegram group you want to monitor

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/VENHEADs/gbp_bot.git
   cd gbp_bot
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot**
   ```bash
   cp config.example.ini config.ini
   # Edit config.ini with your credentials
   ```

5. **Authorize Telegram session**
   ```bash
   python authorize_session.py
   ```

## 🏃 Running the Bot

### Local Development
```bash
# Run directly
python offer_monitor_bot.py

# Or use the convenience script (runs with nohup)
./run_bot.sh

# Stop the bot
./stop_bot.sh
```

### 🐳 Docker
```bash
docker build -t telegram-bot .
docker run -d --name telegram-bot telegram-bot
```

### ☁️ Railway Deployment
See [documentation.md](documentation.md) for detailed Railway deployment instructions.

## 📁 Project Structure

```
├── offer_monitor_bot.py    # Main bot script
├── message_parser.py       # Message parsing logic
├── authorize_session.py    # Session authorization helper
├── config.example.ini      # Configuration template
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── run_bot.sh            # Start script
├── stop_bot.sh           # Stop script
└── sessions/             # Telegram session files
```

## ⚙️ Configuration

Copy `config.example.ini` to `config.ini` and fill in:

- `api_id`: Your Telegram API ID
- `api_hash`: Your Telegram API hash
- `phone_number`: Your phone number
- `target_group_id`: The group to monitor
- `target_topic_id`: Specific topic/thread ID
- `notify_user_id`: Your user ID for notifications

## 🔒 Security

- Never commit `config.ini`, session files, or `env_vars.json`
- Use environment variables for production deployments
- Keep your API credentials secure

## 📝 License

This project is private and proprietary.

## 🤝 Contributing

This is a private project. Please contact the owner for contribution guidelines. 