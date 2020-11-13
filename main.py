from dj_bot import bot

import logging
import pathlib
import sys


# Create the base config file
def create_base_config():
    config_file = open("./config.py", "w")
    config_str: str = "# ----- This is the bot configuration file (CHANGE HERE !) -----\n\n"
    config_str += "DISCORD_TOKEN = \"\"\n"
    config_str += "YOUTUBE_TOKEN = \"\"\n\n"
    config_str += "# Set your os model here (win64 or linux64)\n"
    config_str += "OS = \"linux64\"\n\n"
    config_str += "LOG_FILE = None\n\n"
    config_str += "REQUEST_CHANNEL = \"dj-request\"\n"
    config_str += "PLAYING_CHANNEL = \"general\"\n"
    config_str += "ADMIN_USERS = []\n"
    config_str += "ADMIN_ROLES = []\n"
    config_str += "QUEUE_MAX_SIZE = 30\n"
    config_str += "MAX_RESULT = 10\n"
    config_file.write(config_str)


# The main that configure and start the bot
def main() -> int:
    # Verify the config file
    config_file_path: pathlib.Path = pathlib.Path("./config.py")
    if not config_file_path.is_file():
        create_base_config()

    # Import the config file
    import config

    # Verify the config can work
    if config.DISCORD_TOKEN == "" or config.YOUTUBE_TOKEN == "":
        sys.stderr.write("Cannot start the DJ Bot : "
                         "Please provide correct discord and youtube tokens in the file config.py !\n")
        return 1

    # Configure the logger
    logging.basicConfig(filemode="w", filename=config.LOG_FILE, level=logging.INFO)

    # Create the discord bot
    dj_bot = bot.DJBot(config.DISCORD_TOKEN, config.YOUTUBE_TOKEN, config.OS, config.REQUEST_CHANNEL, config.PLAYING_CHANNEL,
                       config.ADMIN_USERS, config.ADMIN_ROLES, config.QUEUE_MAX_SIZE, config.MAX_RESULT)

    # Start the bot
    dj_bot.start()


# Start the bot
if __name__ == "__main__":
    main()
