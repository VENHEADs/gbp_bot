FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY offer_monitor_bot.py .
COPY message_parser.py .

# Create sessions directory (empty)
RUN mkdir -p /app/sessions

# Run the bot
CMD ["python", "offer_monitor_bot.py"] 