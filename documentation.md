# Project Overview

This project aims to create an automated system to monitor a Telegram group for currency exchange offers (specifically buying RUB or selling GBP) and notify the user, assisting in quickly responding to or creating offers.

## System Architecture Overview

The system will access Telegram by emulating a user account using the Telethon library. This allows access to private groups that the user account is a member of. The system is configured to listen to a specific group ID and, if the group uses topics, a specific topic ID within that group. Configuration is managed via a `config.ini` file. Logging is directed to both the console and a rotating file (`bot.log`).

# Module Map

*   `main.py`: Orchestrates the components, handles Telegram client connection, event listening, notifications, configuration loading, and logging setup.
*   `message_parser.py`: Responsible for analyzing message content to identify relevant offers based on keywords, currency mentions, and amounts.
*   `config.ini`: Stores user-specific credentials and bot settings (not committed to Git).
*   `config.example.ini`: Template for `config.ini`.
*   `requirements.txt`: Lists Python dependencies.
*   `.gitignore`: Specifies intentionally untracked files.
*   `bot.log`: Log output file (not committed to Git).

# How to Run

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
    python main.py
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
    nohup python main.py > bot_console.log 2>&1 &
    ```
    *   `python main.py`: Your command.
    *   `> bot_console.log`: Redirects standard output (prints from the script that would go to console) to `bot_console.log`.
    *   `2>&1`: Redirects standard error (error messages) to the same place as standard output.
    *   `&`: Runs the command in the background.
4.  You can then close the terminal. The script will keep running.
5.  To check its output, you can view `bot_console.log` and `bot.log` (our application log).
6.  To stop a `nohup` process: find its Process ID (PID) using `ps aux | grep main.py` and then use `kill <PID>`.

**Using `screen`:**

`screen` is a terminal multiplexer that allows you to create persistent terminal sessions.

1.  Install `screen` if you don't have it (e.g., `sudo apt install screen` on Debian/Ubuntu, `brew install screen` on macOS).
2.  Start a new screen session: `screen -S telegram_bot_session` (you can name `telegram_bot_session` anything).
3.  Inside the screen session, activate your virtual environment and run the script:
    ```bash
    source .venv/bin/activate
    cd /path/to/your/Telegram Bot
    python main.py
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

*   **YYYY-MM-DD**: Initial setup of Telegram connection (`main.py`) and project documentation (`documentation.md`, `project_milestones.md`).
*   **YYYY-MM-DD**: Implemented message listener in `main.py` for specific group/topic.
*   **YYYY-MM-DD**: Added `message_parser.py` for offer detection; integrated into `main.py`; implemented DM notifications.
*   **YYYY-MM-DD**: Moved credentials to `config.ini`; added file logging; provided instructions for continuous local execution. 