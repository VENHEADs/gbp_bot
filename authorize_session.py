#!/usr/bin/env python3
"""
Session Authorization Script for Railway Deployment

Run this script locally to authorize your Telegram session before deploying to Railway.
The authorized session file will be created in the sessions/ directory.
"""

from telethon import TelegramClient, errors
import asyncio
import os
import configparser

def load_config():
    """Load configuration from config.ini"""
    parser = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        print("🔴 [CRITICAL] config.ini not found!")
        print("Please copy config.example.ini to config.ini and fill in your details.")
        exit(1)
    
    parser.read('config.ini')
    cfg = {}
    try:
        cfg['api_id'] = parser.getint('telegram_credentials', 'api_id')
        cfg['api_hash'] = parser.get('telegram_credentials', 'api_hash')
        cfg['phone_number'] = parser.get('telegram_credentials', 'phone_number')
        cfg['session_name'] = parser.get('bot_settings', 'session_name', fallback='my_telegram_session')
    except Exception as e:
        print(f"🔴 [CRITICAL] Error in config.ini: {e}")
        exit(1)
    
    return cfg

async def main():
    config = load_config()
    
    # Create sessions directory
    sessions_dir = 'sessions'
    if not os.path.exists(sessions_dir):
        os.makedirs(sessions_dir)
        print(f"✅ Created sessions directory: {sessions_dir}")
    
    session_path = os.path.join(sessions_dir, config['session_name'])
    
    print(f"🔐 Authorizing session: {session_path}")
    client = TelegramClient(session_path, config['api_id'], config['api_hash'])
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("📱 Sending authorization code...")
            await client.send_code_request(config['phone_number'])
            code = input("Enter the code sent to your Telegram: ")
            
            try:
                await client.sign_in(config['phone_number'], code)
            except errors.SessionPasswordNeededError:
                password = input("Enter your 2FA password: ")
                await client.sign_in(password=password)
        
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"✅ Successfully authorized as: {me.first_name} {me.last_name or ''} (@{me.username or ''})")
            print(f"✅ Session file created: {session_path}.session")
            print("🚀 You can now deploy to Railway!")
        else:
            print("🔴 Authorization failed!")
            
    except Exception as e:
        print(f"🔴 Error: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main()) 