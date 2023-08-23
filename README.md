# MH Telegram Bot

Welcome to the installation guide for MH Bot, a Telegram bot built using Python!

## Prerequisites

- Python 3.6 or later
- Telegram Bot Token (You can obtain it from the [BotFather](https://core.telegram.org/bots#botfather))
- JSON configuration file (`config.json`) with your bot configuration

## Installation

1. **Clone the Repository:** Begin by cloning this repository to your local machine:

    ```bash
    git clone https://github.com/erpesh/mh-telegram-bot.git
    cd mh-telegram-bot
    ```

2. **Install Dependencies:** Use `pip` to install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure the Bot:**

    - Rename `config-example.json` to `config.json` in the project directory.
    - Open `config.json` and replace `"YOUR_BOT_TOKEN"` with your actual Telegram bot token.
    - Add your `ADMIN_IDS` in the configuration file.

4. **Run the Bot:**

    Start the bot by running the main script:

    ```bash
    python main.py
    ```

    The bot should now be running and listening for incoming messages.

## Bot Usage

Once the bot is up and running, you can interact with it on Telegram:

- Send `/start` to begin using the bot.
- Depending on your user type (admin or regular user), you will have different interaction options.
- Regular users can ask questions and engage in chats with the bot.
- Admins can manage user questions and chats.

## Bot Commands

- `/start`: Start using the bot.
- `/help`: Get help and instructions.
- `/info`: Get information about the bot.
- `/lib`: Access the bot's library.
- `/chat`: Start a chat with an admin (both users and admins can initiate chats).
- `/end`: End the current chat (for admins).
- `/leave`: Leave the chat mode (for admins).
- `/done`: Close a question and move to the next (for admins).
