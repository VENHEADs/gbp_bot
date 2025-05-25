# Project Overview

This project aims to create an automated system to monitor a Telegram group for currency exchange offers (specifically buying RUB or selling GBP) and automatically respond to potential trading partners. The system now includes an auto-response feature that directly messages users looking to buy rubles with a Russian message offering to sell rubles.

## System Architecture Overview

The system will access Telegram by emulating a user account using the Telethon library. This allows access to private groups that the user account is a member of. The system is configured to listen to a specific group ID and, if the group uses topics, a specific topic ID within that group. 

**Key Features:**
- **Message Monitoring**: Listens to a specific Telegram group/topic for currency exchange offers
- **Intelligent Parsing**: Analyzes messages to identify ruble buying offers with high confidence
- **Auto-Response**: Automatically sends a Russian message to users looking to buy rubles: "Привет, если рубли еще нужны, скажи пожалуйста куда перевести, в течении часа переведу"
- **Fallback Notifications**: For non-ruble-buying offers or failed auto-responses, sends notifications to the bot owner
- **Error Handling**: Gracefully handles failed message deliveries and logs all activity

Configuration is managed via a `config.ini` file. Logging is directed to both the console and a rotating file (`bot.log`). The main script is `offer_monitor_bot.py`.

# Module Map

*   `offer_monitor_bot.py`: Orchestrates the components, handles Telegram client connection, event listening, notifications, configuration loading, and logging setup.
*   `message_parser.py`: Responsible for analyzing message content to identify relevant offers based on keywords, currency mentions, and amounts.
*   `config.ini`: Stores user-specific credentials and bot settings (not committed to Git).
*   `config.example.ini`: Template for `config.ini`.
*   `requirements.txt`: Lists Python dependencies.
*   `.gitignore`: Specifies intentionally untracked files.
*   `bot.log`: Log output file (not committed to Git).

# How to Run

## Railway Cloud Deployment

### Prerequisites
1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Push your code to GitHub
3. **Authorized Session**: Run session authorization locally first

### Step 1: Authorize Session Locally
Before deploying to Railway, you must authorize your Telegram session locally:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run session authorization script
python authorize_session.py
```

This creates an authorized session file in `sessions/` directory that will be used by Railway.

### Step 2: Deploy to Railway
1. **Connect Repository**:
   - Go to [railway.app](https://railway.app) and create new project
   - Connect your GitHub repository
   - Railway will auto-detect the Dockerfile

2. **Set Environment Variables**:
   In Railway dashboard, add these environment variables:
   ```
   API_ID=your_api_id_here
   API_HASH=your_api_hash_here
   PHONE_NUMBER=your_phone_number_here
   TARGET_GROUP_ID=your_target_group_id_here
   TARGET_TOPIC_ID=your_target_topic_id_here
   NOTIFY_USER_ID=your_notify_user_id_here
   SESSION_NAME=my_telegram_session
   ```

3. **Deploy**:
   - Railway will automatically build and deploy your bot
   - Monitor logs in Railway dashboard to ensure successful startup

### Step 3: Monitor Deployment
- Check Railway logs for successful Telegram connection
- Verify bot responds to messages in your target group
- Monitor auto-response functionality

## Initial Setup

1.  **Clone/Set up Project**: Ensure you have all project files.
2.  **Create Telegram Application** (if not done already):
    *   Go to [https://my.telegram.org/apps](https://my.telegram.org/apps) and log in.
    *   Create a new application to obtain your `api_id` and `api_hash`.
3.  **Create and Configure `config.ini`**:
    *   Copy `config.example.ini` to a new file named `config.ini` in the project root.
    *   Open `config.ini` and fill in all the required values under `[telegram_credentials]` and `[bot_settings]`:
        *   `api_id`, `api_hash`, `phone_number`
        *   `target_group_id` (ID of the main Telegram group)
        *   `target_topic_id` (ID of the specific topic within the group)
        *   `notify_user_id` (Your Telegram User ID for receiving notifications)
        *   `session_name` (Default is `my_telegram_session`. This is the base name for the Telethon session file that will be created, e.g., `my_telegram_session.session`)
4.  **Create and Activate Virtual Environment** (from the project root directory):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
5.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Script

1.  **Activate Virtual Environment** (if not already active):
    ```bash
    source .venv/bin/activate
    ```
2.  **Run the main script**:
    ```bash
    python offer_monitor_bot.py
    ```
    *   The first time you run it after configuring `config.ini` (or if the `.session` file is deleted), you may be prompted for a login code sent to your Telegram account and your 2FA password if enabled.
    *   A session file (e.g., `my_telegram_session.session`) will be created to store login information.
    *   The script will then listen for messages. Logs will appear on the console (INFO and above) and in `bot.log` (DEBUG and above).

## Running Continuously (Local Machine - macOS/Linux)

To keep the script running on your local machine even after you close the terminal or get disconnected, you can use tools like `nohup` or `screen`.

**Using `nohup` (No Hang Up):**

`nohup` runs a command immune to hangups, with output to a `nohup.out` file by default if not redirected.

1.  Activate your virtual environment: `source .venv/bin/activate`
2.  Navigate to the project directory: `cd /path/to/your/Telegram Bot`
3.  Run the script with `nohup`:
    ```bash
    nohup python offer_monitor_bot.py > bot_console.log 2>&1 &
    ```
    *   `python offer_monitor_bot.py`: Your command.
    *   `> bot_console.log`: Redirects standard output (prints from the script that would go to console) to `bot_console.log`.
    *   `2>&1`: Redirects standard error (error messages) to the same place as standard output.
    *   `&`: Runs the command in the background.
4.  You can then close the terminal. The script will keep running.
5.  To check its output, you can view `bot_console.log` and `bot.log` (our application log).
6.  To stop a `nohup` process: find its Process ID (PID) using `ps aux | grep offer_monitor_bot.py` and then use `kill <PID>`.

**Using `screen`:**

`screen` is a terminal multiplexer that allows you to create persistent terminal sessions.

1.  Install `screen` if you don't have it (e.g., `sudo apt install screen` on Debian/Ubuntu, `brew install screen` on macOS).
2.  Start a new screen session: `screen -S telegram_bot_session` (you can name `telegram_bot_session` anything).
3.  Inside the screen session, activate your virtual environment and run the script:
    ```bash
    source .venv/bin/activate
    cd /path/to/your/Telegram Bot
    python offer_monitor_bot.py
    ```
4.  **Detach from the screen session**: Press `Ctrl+A` then `Ctrl+D`. The script continues running in this detached session.
5.  You can now close your main terminal.
6.  **To reattach** to the session later (e.g., to see output or stop it):
    *   List screen sessions: `screen -ls`
    *   Reattach: `screen -r telegram_bot_session` (or use the PID if multiple sessions)
7.  **To stop the script**: Reattach to the screen session and press `Ctrl+C`.
8.  **To terminate the screen session** (after stopping the script): Type `exit` in the screen session.

Choose the method (`nohup` or `screen`) that you find more convenient.

# Change Log

*   **YYYY-MM-DD**: Initial setup of Telegram connection and project documentation.
*   **YYYY-MM-DD**: Implemented message listener for specific group/topic.
*   **YYYY-MM-DD**: Added `message_parser.py`; integrated parsing; implemented DM notifications.
*   **YYYY-MM-DD**: Moved credentials to `config.ini`; added file logging; provided local execution guide.
*   **2024-05-09**: Initialized Git repository. Committed first functional version.
*   **2024-05-09**: Renamed main script from `main.py` to `offer_monitor_bot.py` for clarity.
*   **2025-01-XX**: Implemented auto-response feature - bot now automatically sends Russian message to users looking to buy rubles instead of just notifying bot owner. Added intelligent filtering to only respond to 'counterparty_buys_rub' offers with high/medium confidence. Added error handling and fallback to notifications if auto-response fails.
*   **2025-01-XX**: Added Railway cloud deployment support - migrated config to environment variables, implemented session file persistence, created Dockerfile and railway.toml, added deployment scripts and documentation for 24/7 cloud hosting. 