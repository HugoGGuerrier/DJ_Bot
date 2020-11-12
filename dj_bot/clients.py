from dj_bot import LOGGER_NAME
from dj_bot import bot
from dj_bot import command
from dj_bot import song

import discord
import googleapiclient.discovery
import logging
import re


# This class is the custom discord client to handle interaction with users
class DJDiscordClient(discord.Client):

    # ----- Constructor -----

    def __init__(self, dj_bot, request_channel: str, admin_users: list, admin_roles: list):
        # Call the super constructor
        super().__init__()

        # Assign attributes
        self.dj_bot: bot.DJBot = dj_bot
        self.req_chan_name = request_channel
        self.req_chan: discord.TextChannel = None
        self.admin_users: list = admin_users
        self.admin_roles: list = admin_roles

    # ----- Class methods -----

    # Process a command to the bot
    def process_command(self, message: discord.Message) -> None:
        # Extract the command from the message
        com: command.Command = command.Command(message.content)

        # Handle every command
        if com.name == "!help":
            self.dj_bot.show_help()
        elif com.name == "!play":
            self.dj_bot.add_music(song.Song(com.arg))
        elif com.name == "!stop":
            self.dj_bot.stop_music()
        elif com.name == "!queue":
            self.dj_bot.show_queue()
        elif com.name == "!search":
            self.dj_bot.show_search(com.arg)
        elif com.name == "!choose":
            self.dj_bot.choose_search(com.arg)
        elif com.name == "!empty-queue":
            self.dj_bot.empty_queue()
        elif com.name == "!shutdown":
            self.dj_bot.stop()

    async def send_message(self, message: str) -> None:
        # Get the request channel object if it not exists
        if self.req_chan is None:
            self.req_chan = discord.utils.get(self.get_all_channels(), name=self.req_chan_name)

        # Send the message
        await self.req_chan.send(content=message)

    # ------ Handling methods -----

    # Log the bot ready state
    async def on_ready(self) -> None:
        logging.getLogger(LOGGER_NAME).info("DJ Bot is started and ready, listen to " + self.req_chan_name)

    # Handle a new message
    async def on_message(self, message: discord.Message) -> None:
        if message.channel.name == self.req_chan_name:
            self.process_command(message)


# This class handles all youtube requests
class DJYoutubeClient:

    # ----- Constructor -----

    def __init__(self, dj_bot, youtube_token: str):
        # Assign the attributes
        self.dj_bot: bot.DJBot = dj_bot
        self.youtube_token: str = youtube_token

        # Create the youtube client
        self.client = googleapiclient.discovery.build("youtube", "v3", developerKey=self.youtube_token)

    # ----- Class methods -----

    def parse_time(self, yt_time: str) -> str:
        res: list = list()
        tmp = re.sub("[H|M]", ":", yt_time[2:-1]).split(":")
        for t in tmp:
            if len(t) == 1:
                t = "0" + t
            res.append(t)
        return ":".join(res)

    def search_videos(self, query: str, max_results: int) -> dict:
        # Prepare the request
        search_req = self.client.search().list(
            part="snippet",
            maxResults=max_results,
            q=query,
            type="video"
        )

        # Get the raw result of the search
        raw_result = search_req.execute()

        # Prepare the final result
        final_result: dict = dict()

        for raw_item in raw_result["items"]:
            final_item = dict()
            final_item["title"] = raw_item["snippet"]["title"]
            final_item["channel_title"] = raw_item["snippet"]["channelTitle"]
            final_item["description"] = raw_item["snippet"]["description"]
            final_result[raw_item["id"]["videoId"]] = final_item

        # Get the video's duration
        precision_req = self.client.videos().list(
            part="contentDetails",
            id=",".join(final_result.keys())
        )

        # Get the raw result of the video precisions
        raw_result = precision_req.execute()

        for raw_item in raw_result["items"]:
            video_id = raw_item["id"]
            final_result[video_id]["duration"] = self.parse_time(raw_item["contentDetails"]["duration"])

        # Return the final list
        return final_result
