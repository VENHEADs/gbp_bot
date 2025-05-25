FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY offer_monitor_bot.py .
COPY message_parser.py .

# Create required directories
RUN mkdir -p sessions

# Set environment
ENV PYTHONUNBUFFERED=1

# Add a simple health check script
RUN echo '#!/bin/sh\nexit 0' > /healthcheck.sh && chmod +x /healthcheck.sh

# Run the bot
CMD ["python", "offer_monitor_bot.py"] 