FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY offer_monitor_bot.py .
COPY message_parser.py .

# Create sessions directory
RUN mkdir -p /app/sessions

# Set Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "offer_monitor_bot.py"] 