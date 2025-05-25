FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY offer_monitor_bot.py .
COPY message_parser.py .

# Copy the authorized session file
COPY sessions/my_telegram_session.session /app/sessions/my_telegram_session.session

# Run the bot
CMD ["python", "offer_monitor_bot.py"] 