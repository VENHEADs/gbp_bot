FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# create directory for session files
RUN mkdir -p /app/sessions

CMD ["python", "offer_monitor_bot.py"] 