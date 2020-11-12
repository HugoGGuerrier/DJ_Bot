import config
from dj_bot import bot

import logging

# To remove
from dj_bot import command


# The main that configure and start the bot
def main():
    # Configure the logger
    logging.basicConfig(filemode="w", filename=config.LOG_FILE, level=logging.INFO)

    # Create the discord bot
    dj_bot = bot.DJBot(config.DISCORD_TOKEN, config.YOUTUBE_TOKEN, config.REQUEST_CHANNEL, config.ADMIN_USERS,
                       config.ADMIN_ROLES, config.QUEUE_MAX_SIZE)

    # Start the bot
    dj_bot.start()


# Start the bot
if __name__ == "__main__":
    main()
