# Railway Session Setup Instructions

Since session files contain sensitive authentication data, they should NOT be committed to public repositories.

## Option 1: Railway Volume Upload (Recommended)

1. **Create a Railway Volume**:
   - In Railway dashboard, go to your service
   - Click "Settings" → "Volumes"
   - Create a new volume mounted at `/app/sessions`

2. **Upload Session File**:
   - Use Railway CLI or dashboard to upload your local session file
   - Upload `sessions/my_telegram_session.session` to the volume

## Option 2: Base64 Environment Variable

1. **Encode Session File**:
   ```bash
   base64 sessions/my_telegram_session.session > session_base64.txt
   ```

2. **Add to Railway Environment Variables**:
   - Variable: `SESSION_BASE64`
   - Value: [contents of session_base64.txt]

3. **Modify bot to decode on startup** (see railway_session_decoder.py)

## Option 3: Re-authorize on Railway (Current Setup)

The bot will prompt for authorization on first Railway run:
- Check Railway logs for authorization prompts
- This requires manual intervention but is most secure 