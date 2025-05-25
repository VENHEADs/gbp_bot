#!/usr/bin/env python3
from telethon import TelegramClient
import asyncio
import configparser
import os

async def revoke_session():
    parser = configparser.ConfigParser()
    parser.read('config.ini')
    api_id = parser.getint('telegram_credentials', 'api_id')
    api_hash = parser.get('telegram_credentials', 'api_hash')
    
    client = TelegramClient('temp_revoke', api_id, api_hash)
    await client.connect()
    
    if await client.is_user_authorized():
        await client.log_out()
        print('✅ Session revoked successfully')
    else:
        print('Session was already invalid')
    
    await client.disconnect()
    
    # Clean up temp session file
    if os.path.exists('temp_revoke.session'):
        os.remove('temp_revoke.session')

if __name__ == '__main__':
    asyncio.run(revoke_session()) 