FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY offer_monitor_bot.py .
COPY message_parser.py .

# Create sessions directory
RUN mkdir -p sessions

# Run the bot
CMD ["python", "offer_monitor_bot.py"] 