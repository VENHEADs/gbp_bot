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
    cfg = {}
    
    # Try to load from environment variables first (for Railway deployment)
    if os.getenv('API_ID'):
        try:
            cfg['api_id'] = int(os.getenv('API_ID'))
            cfg['api_hash'] = os.getenv('API_HASH')
            cfg['phone_number'] = os.getenv('PHONE_NUMBER')
            cfg['target_group_id'] = int(os.getenv('TARGET_GROUP_ID'))
            cfg['target_topic_id'] = int(os.getenv('TARGET_TOPIC_ID'))
            cfg['notify_user_id'] = int(os.getenv('NOTIFY_USER_ID'))
            cfg['session_name'] = os.getenv('SESSION_NAME', 'my_telegram_session')
            print("✅ Configuration loaded from environment variables")
            return cfg
        except (ValueError, TypeError) as e:
            print(f"🔴 [CRITICAL] Error parsing environment variables: {e}")
            exit(1)
    
    # Fallback to config.ini for local development
    parser = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        print("🔴 [CRITICAL] config.ini not found and no environment variables set!")
        print("Please copy config.example.ini to config.ini and fill in your details.")
        exit(1)
    
    parser.read('config.ini')
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
       str(cfg['target_group_id']) == 'GROUP_ID_OF_THE_TARGET_CHAT':
        print("🔴 [CRITICAL] Placeholder values found in config.ini.")
        print("Please replace all YOUR_..._HERE placeholders with your actual values.")
        exit(1)
    
    print("✅ Configuration loaded from config.ini")
    return cfg

def setup_session_from_env(session_name):
    """Decode base64 session from environment variable if available"""
    session_b64 = os.getenv('SESSION_BASE64')
    if not session_b64:
        print("No SESSION_BASE64 environment variable found")
        return False
        
    try:
        import base64
        print(f"Found SESSION_BASE64 environment variable (length: {len(session_b64)})")
        
        # Decode base64 data
        session_data = base64.b64decode(session_b64)
        print(f"Successfully decoded base64 data (size: {len(session_data)} bytes)")
        
        # Create sessions directory
        os.makedirs('sessions', exist_ok=True)
        
        # Write session file
        session_path = os.path.join('sessions', session_name + '.session')
        with open(session_path, 'wb') as f:
            f.write(session_data)
        
        # Verify file was written
        if os.path.exists(session_path):
            file_size = os.path.getsize(session_path)
            print(f"✅ Session restored from environment variable to {session_path} ({file_size} bytes)")
            return True
        else:
            print(f"🔴 Failed to write session file to {session_path}")
            return False
            
    except Exception as e:
        print(f"🔴 Failed to restore session from environment: {e}")
        import traceback
        traceback.print_exc()
        return False

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

# Create sessions directory if it doesn't exist (for cloud deployment)
sessions_dir = 'sessions'
if not os.path.exists(sessions_dir):
    os.makedirs(sessions_dir)
    logger.info(f"Created sessions directory: {sessions_dir}")

# Use sessions directory for session file
session_path = os.path.join(sessions_dir, SESSION_NAME)

# Restore session from environment if available (MUST happen before TelegramClient creation)
session_restored = setup_session_from_env(SESSION_NAME)
if session_restored:
    logger.info("Session successfully restored from environment variable")
else:
    logger.info("No session restoration needed (running locally or session already exists)")

# Check if session file exists after restoration attempt
if os.path.exists(session_path):
    logger.info(f"Session file found at: {session_path}")
else:
    logger.warning(f"No session file at: {session_path}")

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
            
            parsed_offer = parse_message_for_offer(message.text)
            
            if parsed_offer:
                logger.info(f"  Parsed Offer: {parsed_offer}")
                # Construct and send notification
                offer_type = parsed_offer.get("offer_type", "N/A")
                confidence = parsed_offer.get("confidence", "N/A")
                amount_gbp = parsed_offer.get("amount_gbp", "N/A")
                amount_rub = parsed_offer.get("amount_rub", "N/A")
                original_msg_text = parsed_offer.get("original_message", "Error fetching original message.")

                # Store sender information for potential auto-response
                sender_id = sender.id if sender else None
                sender_username = getattr(sender, 'username', None)

                # Check if this is a ruble buying offer that should trigger auto-response
                should_auto_respond = (offer_type == "counterparty_buys_rub" and 
                                     confidence in ["high", "medium"] and 
                                     sender_id is not None)

                if should_auto_respond:
                    # Send auto-response to the person looking to buy rubles
                    auto_response_text = "Привет, если рубли еще нужны, скажи пожалуйста куда перевести, в течении часа переведу"
                    
                    try:
                        await client.send_message(sender_id, auto_response_text)
                        logger.info(f"Auto-response sent to {sender_name} (ID: {sender_id}) for ruble buying offer.")
                    except Exception as e:
                        logger.error(f"Failed to send auto-response to {sender_name} (ID: {sender_id}): {e}")
                        # If auto-response fails, fall back to notification to bot owner
                        should_auto_respond = False

                # If not auto-responding or auto-response failed, send notification to bot owner
                if not should_auto_respond:
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
    client = TelegramClient(session_path, API_ID, API_HASH)

    try:
        logger.info("Initializing Telegram client...")
        logger.info(f"Session path: {session_path}")
        logger.info(f"Session file exists: {os.path.exists(session_path)}")
        
        await client.connect()
        logger.info("Connected to Telegram successfully")
        
        if not await client.is_user_authorized():
            # Check if running locally (config.ini exists) or in cloud (env vars)
            is_local_run = os.path.exists('config.ini') and not os.getenv('API_ID')
            
            if is_local_run:
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
                logger.error("Session not authorized. This indicates a problem with session restoration.")
                logger.error(f"Session file exists: {os.path.exists(session_path)}")
                if os.path.exists(session_path):
                    logger.error(f"Session file size: {os.path.getsize(session_path)} bytes")
                logger.error("For Railway deployment, session must be pre-authorized and properly restored.")
                logger.error("Check that SESSION_BASE64 environment variable is correctly set.")
                return
        else:
            logger.info("User is already authorized.")

        me = await client.get_me()
        logger.info(f"Successfully connected as: {me.first_name}")
        
        # Start the event listener
        await run_listener(client)
        logger.info("Event listener started. Running until disconnected...")
        await client.run_until_disconnected()

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()

if __name__ == '__main__':
    # The initial check for placeholder API_ID etc. is now done in load_config()
    asyncio.run(main()) 