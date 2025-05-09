#!/usr/bin/env python3
from telethon import TelegramClient, errors, events
import asyncio
import logging
import logging.handlers # For RotatingFileHandler
import configparser
import os
from message_parser import parse_message_for_offer

# --- Configuration Loading ---
def load_config():
    parser = configparser.ConfigParser()
    # Ensure config.ini exists, if not, guide user to create from example
    if not os.path.exists('config.ini'):
        print("🔴 [CRITICAL] config.ini not found! ")
        print("Please copy config.example.ini to config.ini and fill in your details.")
        exit(1)
    parser.read('config.ini')
    cfg = {}
    try:
        cfg['api_id'] = parser.getint('telegram_credentials', 'api_id')
        cfg['api_hash'] = parser.get('telegram_credentials', 'api_hash')
        cfg['phone_number'] = parser.get('telegram_credentials', 'phone_number')
        
        cfg['target_group_id'] = parser.getint('bot_settings', 'target_group_id')
        cfg['target_topic_id'] = parser.getint('bot_settings', 'target_topic_id')
        cfg['notify_user_id'] = parser.getint('bot_settings', 'notify_user_id')
        cfg['session_name'] = parser.get('bot_settings', 'session_name', fallback='my_telegram_session')
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print(f"🔴 [CRITICAL] Error in config.ini: {e}")
        print("Please ensure config.ini is correctly formatted based on config.example.ini.")
        exit(1)
    
    # Validate that placeholder values have been changed
    if cfg['api_id'] == 'YOUR_API_ID_HERE' or \
       str(cfg['target_group_id']) == 'GROUP_ID_OF_THE_TARGET_CHAT': # Check one example
        print("🔴 [CRITICAL] Placeholder values found in config.ini.")
        print("Please replace all YOUR_..._HERE placeholders with your actual values.")
        exit(1)
    return cfg

config = load_config()

# --- Logging Setup ---
logger = logging.getLogger(__name__) # Get logger for this module
# Prevent Telethon from flooding logs unless it's an error
logging.getLogger('telethon').setLevel(logging.ERROR)

log_formatter = logging.Formatter('[%(levelname)5s/%(asctime)s] %(name)s: %(message)s')

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO) # Set console to INFO

# File Handler (Rotating)
log_file = 'bot.log'
file_handler = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=5*1024*1024, backupCount=2 # 5MB per file, 2 backups
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG) # Log DEBUG and above to file

# Get the root logger and add handlers
root_logger = logging.getLogger() 
root_logger.setLevel(logging.DEBUG) # Set root logger to DEBUG to allow file handler to catch DEBUG
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# --- Telegram Client Setup (using loaded config) ---
API_ID = config['api_id']
API_HASH = config['api_hash']
PHONE_NUMBER = config['phone_number']
SESSION_NAME = config['session_name']
TARGET_GROUP_ID = config['target_group_id']
TARGET_TOPIC_ID = config['target_topic_id']
NOTIFY_USER_ID = config['notify_user_id']

async def run_listener(client: TelegramClient):
    logger.info(f"Listening to Group ID: {TARGET_GROUP_ID}, specifically for Topic ID: {TARGET_TOPIC_ID}")

    @client.on(events.NewMessage(chats=TARGET_GROUP_ID))
    async def new_message_handler(event):
        message = event.message
        actual_topic_id = None
        is_topic_message_context = False

        # --- Topic ID Determination Logic (simplified logging) ---
        if hasattr(message, 'topic_id') and message.topic_id:
            actual_topic_id = message.topic_id
            is_topic_message_context = True
        elif message.reply_to:
            if hasattr(message.reply_to, 'reply_to_top_id') and message.reply_to.reply_to_top_id is not None:
                actual_topic_id = message.reply_to.reply_to_top_id
                is_topic_message_context = True
            elif getattr(message.reply_to, 'forum_topic', False) and hasattr(message.reply_to, 'reply_to_msg_id') and message.reply_to.reply_to_msg_id is not None:
                actual_topic_id = message.reply_to.reply_to_msg_id
                is_topic_message_context = True
        # --- End of Topic ID Determination Logic ---

        if is_topic_message_context and actual_topic_id == TARGET_TOPIC_ID:
            sender = await message.get_sender()
            sender_name = (f"{sender.first_name} {sender.last_name or ''}").strip() if sender else "Unknown Sender"
            
            logger.info(f"==== TARGET TOPIC MESSAGE from {sender_name} ====")
            logger.info(f"  Original Text: {message.text}")
            
            parsed_offer = parseo_message_for_offer(message.text)
            
            if parsed_offer:
                logger.info(f"  Parsed Offer: {parsed_offer}")
                # Construct and send notification
                offer_type = parsed_offer.get("offer_type", "N/A")
                confidence = parsed_offer.get("confidence", "N/A")
                amount_gbp = parsed_offer.get("amount_gbp", "N/A")
                amount_rub = parsed_offer.get("amount_rub", "N/A")
                original_msg_text = parsed_offer.get("original_message", "Error fetching original message.")

                # Construct deep link to the message if possible
                # Format: https://t.me/c/CHAT_ID/MSG_ID (CHAT_ID without -100 prefix)
                # Or for groups with username: https://t.me/GROUP_USERNAME/MSG_ID
                # This requires knowing if the group is public/has a username, or its specific chat_id structure.
                # For now, we'll skip the deep link and focus on the text.
                
                # Try to get a link to the message
                msg_link = f"https://t.me/c/{str(message.chat_id).replace('-100', '')}/{message.id}"
                # Check if chat has a username for a potentially more stable link
                if hasattr(message.chat, 'username') and message.chat.username:
                    msg_link = f"https://t.me/{message.chat.username}/{message.id}"

                notification_lines = [
                    "🔔 *New Exchange Offer Alert!* 🔔",
                    "-------------------------------------",
                    f"*Type*: {offer_type.replace('_', ' ').title()}",
                    f"*Confidence*: {confidence.title()}",
                    f"*GBP Amount*: {amount_gbp}",
                    f"*RUB Amount*: {amount_rub}",
                    "-------------------------------------",
                    f"*Original Message (from {sender_name})*:",
                    f"> {original_msg_text}",
                    "-------------------------------------",
                    f"Link to message: {msg_link}"
                ]
                notification_text = "\n".join(notification_lines)
                
                try:
                    await client.send_message(NOTIFY_USER_ID, notification_text, parse_mode='md') # Using Markdown
                    logger.info(f"Notification sent to User ID {NOTIFY_USER_ID} for message ID {message.id}.")
                except Exception as e:
                    logger.error(f"Failed to send notification message: {e}")
            else:
                logger.info("  Parser Result: No relevant offer identified by parser.")
            logger.info("==============================================")
        elif is_topic_message_context:
            logger.debug(f"--- IGNORING (Wrong Topic) --- Deduced Topic {actual_topic_id}. Text: {message.text[:60]}...")
        else:
            logger.debug(f"--- IGNORING (No/Unknown Topic Context) --- Text: {message.text[:60]}...")

async def main():
    logger.info(f"Initializing Telegram client for session: {SESSION_NAME} (from config)")
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    try:
        logger.info("Connecting to Telegram...")
        await client.connect()
        if not await client.is_user_authorized():
            logger.info("User not authorized. Attempting sign-in...")
            try:
                await client.send_code_request(PHONE_NUMBER)
                code = input("Telegram sent a code. Please enter it: ")
                await client.sign_in(PHONE_NUMBER, code)
            except errors.SessionPasswordNeededError:
                password = input("2FA password needed: ")
                await client.sign_in(password=password)
            if not await client.is_user_authorized():
                logger.error("Still not authorized. Exiting.")
                return
            logger.info("Re-authorized successfully.")
        else:
            logger.info("User is already authorized.")

        me = await client.get_me()
        logger.info(f"Successfully connected as: {me.first_name} {me.last_name or ''} (@{me.username or ''})")
        
        # Start the event listener (passing the initialized client)
        # The listener will now run indefinitely using client.run_until_disconnected() internally within its own logic if needed,
        # but here we attach handlers and then keep main alive.
        await run_listener(client) # Call the function that sets up the event handler
        logger.info("Event listener started. Running until disconnected...")
        await client.run_until_disconnected()

    except errors.RpcError as e:
        logger.error(f"Telegram API RPC Error: {e} (Type: {type(e)})")
    except ConnectionError as e:
        logger.error(f"Connection Error: {e}. Check your internet connection.")
    except KeyboardInterrupt:
        logger.info("Listener stopped by user (Ctrl+C).")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
    finally:
        if client.is_connected():
            logger.info("Disconnecting client...")
            await client.disconnect()
            logger.info("Client disconnected.")

if __name__ == '__main__':
    # The initial check for placeholder API_ID etc. is now done in load_config()
    asyncio.run(main()) 