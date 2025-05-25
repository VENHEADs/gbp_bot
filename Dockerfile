FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary application files
COPY offer_monitor_bot.py .
COPY message_parser.py .

# Create required directories
RUN mkdir -p sessions

# Set environment to production
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "offer_monitor_bot.py"] 