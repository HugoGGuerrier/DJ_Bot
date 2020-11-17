from dj_bot import bot, command, song, utils
from dj_bot import LOGGER_NAME, DOWNLOAD_DIR, CACHE_FILE

import discord
import googleapiclient.discovery
import youtube_dl as yt
import logging
import threading
import html


class DJDiscordClient(discord.Client):
    """
    DJDiscordClient class.

    This class is the custom discord client for the DJ Bot, it handles all interactions with discord
    """

    # ----- Constructor -----

    def __init__(self, dj_bot, request_channel: str, playing_channel: str, remove_req: bool):
        """
        Create a new discord client with the request and the playing channel

        params :
            - dj_bot: dj_bot.DJBot = The bot that contains the client
            - request_channel: str = The request channel name
            - playing_channel: str = The playing channel name
        """

        # Call the super constructor
        super().__init__()

        # Assign attributes
        self.dj_bot: bot.DJBot = dj_bot
        self.req_chan_name: str = request_channel
        self.play_chan_name: str = playing_channel
        self.remove_req: bool = remove_req
        self.req_chan: discord.TextChannel = None
        self.play_chan: discord.VoiceChannel = None
        self.play_chan_client: discord.VoiceClient = None

    # ----- Class methods -----

    def process_command(self, message: discord.Message) -> None:
        """
        Extract and process a command from a discord message

        params :
            - message: discord.Message = The message to process
        """

        # Extract the command from the message
        com: command.Command = command.Command(message.content)

        # Handle every command
        if com.name == "!help" or com.name == "!h":
            self.dj_bot.show_help()
        elif com.name == "!play" or com.name == "!pl":
            self.dj_bot.add_music(com.arg, message.author)
        elif com.name == "!skip" or com.name == "!sk":
            self.dj_bot.skip_music()
        elif com.name == "!pause" or com.name == "!pa":
            self.dj_bot.pause_music()
        elif com.name == "!resume" or com.name == "!re":
            self.dj_bot.resume_music()
        elif com.name == "!current" or com.name == "!cu":
            self.dj_bot.show_current()
        elif com.name == "!queue" or com.name == "!qu":
            self.dj_bot.show_queue()
        elif com.name == "!pop":
            self.dj_bot.pop_queue(com.arg)
        elif com.name == "!search" or com.name == "!se":
            self.dj_bot.show_search(com.arg, message.author)
        elif com.name == "!choose" or com.name == "!ch":
            self.dj_bot.choose_search(com.arg, message.author)
        elif com.name == "!ban":
            self.dj_bot.ban_user(com.arg, message.author)
        elif com.name == "!unban":
            self.dj_bot.unban_user(com.arg, message.author)
        elif com.name == "!shame":
            self.dj_bot.show_banned(message.author)
        elif com.name == "!empty-queue":
            self.dj_bot.empty_queue(message.author)
        elif com.name == "!clean-cache":
            self.dj_bot.clean_song_cache(message.author)
        elif com.name == "!shutdown":
            self.dj_bot.shutdown(message.author)

        # Remove the request message to keep the board clean
        if com.name != "!shutdown" and com.name != "" and self.remove_req:
            try:
                self.loop.create_task(message.delete())
            except discord.Forbidden as _:
                logging.getLogger(LOGGER_NAME).warning(
                    "Cannot remove message from the listening channel : Forbidden")
            except discord.NotFound as _:
                pass
            except discord.HTTPException as _:
                logging.getLogger(LOGGER_NAME).warning(
                    "Cannot remove message from the listening channel : HTTPError")

    def send_message(self, message: str) -> None:
        """
        Send a simple message

        params :
            - message: str = The message to send
        """

        # Create a new sending message task
        self.loop.create_task(self.req_chan.send(content=message))

    def play_song(self, sng: song.Song):
        """
        Start playing the wanted song

        params :
            - sng: song.Song = The song you want to play
        """

        self.play_chan_client.play(sng.get_audio_source(), after=self.dj_bot.next_in_queue)

    def stop_song(self):
        """
        Stop the current song and clear the audio source
        """

        if self.play_chan_client.is_playing() or self.play_chan_client.is_paused():
            self.play_chan_client.stop()

    def pause_song(self):
        """
        Pause the current song
        """

        if self.play_chan_client.is_playing():
            self.play_chan_client.pause()

    def resume_song(self):
        """
        Resume the current song
        """

        if self.play_chan_client.is_paused():
            self.play_chan_client.resume()

    def disconnect(self):
        """
        Disconnect the bot from the discord server
        """

        self.stop_song()
        self.play_chan_client.cleanup()
        self.loop.create_task(self.play_chan_client.disconnect())

    # ------ Handling methods -----

    async def on_ready(self) -> None:
        """
        Function called when the bot is ready to listen
        """

        # Get the request channel
        self.req_chan = discord.utils.get(self.get_all_channels(), name=self.req_chan_name)

        # Get the playing channel and connect to it
        self.play_chan = discord.utils.get(self.get_all_channels(), name=self.play_chan_name)
        self.play_chan_client = await self.play_chan.connect()

        # Log the bot state
        logging.getLogger(LOGGER_NAME).info("DJ Bot is started and ready, listen to " + self.req_chan_name)

        # Load the previous bot state
        self.dj_bot.load()

    async def on_message(self, message: discord.Message) -> None:
        """
        Function called when a new message arrive

        params :
            - message: discord.Message = The new message
        """

        # Verify the message channel and the user banning state
        if message.channel.name == self.req_chan_name and not self.dj_bot.is_banned(message.author):
            self.process_command(message)


class DJYoutubeClient:
    """
    DJYoutubeClient class.

    This class contains all methods for the bot to gather information and data from Youtube
    """

    # ----- Constructor -----

    def __init__(self, dj_bot, youtube_token: str):
        """
        Construct a new client with the parent bot and the wanted token

        params :
            - dj_bot: dj_bot.DJBot = The parent bot
            - youtube_token: str = The Youtube Data API v3 token
        """

        # Assign the attributes
        self.dj_bot: bot.DJBot = dj_bot
        self.youtube_token: str = youtube_token

        # Create the youtube client
        self.client = googleapiclient.discovery.build("youtube", "v3", developerKey=self.youtube_token)

        # Set the youtube dl options
        self.ytdl_opts: dict = {
            "outtmpl": DOWNLOAD_DIR + "%(id)s.%(ext)s",
            "logger": logging.getLogger(LOGGER_NAME),
            "download_archive": CACHE_FILE,
            "format": "mp4"
        }

    # ----- Class methods -----

    def search_videos(self, query: str, max_results: int) -> list:
        """
        Get all videos and their details with a search phrase

        params :
            - query: str = The search phrase
            max_results: int = The maximum number of results

        return -> list = A list of the youtube result
        """

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
        final_result: list = list()
        video_id_list: list = list()

        for raw_item in raw_result["items"]:
            final_item = dict()
            final_item["id"] = raw_item["id"]["videoId"]
            final_item["title"] = html.unescape(raw_item["snippet"]["title"])
            final_item["channel_title"] = html.unescape(raw_item["snippet"]["channelTitle"])
            final_item["description"] = html.unescape(raw_item["snippet"]["description"])

            video_id_list.append(raw_item["id"]["videoId"])
            final_result.append(final_item)

        # Get the video's duration
        precision_req = self.client.videos().list(
            part="contentDetails",
            id=",".join(video_id_list)
        )

        # Get the raw result of the video precisions
        raw_result = precision_req.execute()

        for i in range(len(raw_result["items"])):
            video_duration = raw_result["items"][i]["contentDetails"]["duration"]
            final_result[i]["duration"] = utils.parse_youtube_time(video_duration)

        # Return the final list
        return final_result

    def get_first_video(self, title: str) -> dict:
        """
        Get the first Youtube result for a title

        params :
            - title: str = the title you want to search
        """

        return self.search_videos(title, 1)[0]

    def download_song(self, sng: song.Song):
        """
        Download a song an set its state to ready when the download is finished

        params :
            - sng: song.Song = The song to download
        """

        # Prepare the youtube downloader
        ytdl: yt.YoutubeDL = yt.YoutubeDL(self.ytdl_opts)
        ytdl.add_progress_hook(sng.download_hook)

        # Verify that the song is not in the cache
        if not ytdl.in_download_archive({"id": sng.video_id, "extractor_key": "youtube"}):
            # Create the video URL
            video_url = "https://www.youtube.com/watch?v=" + sng.video_id

            # Start the video downloading in a thread to avoid waiting
            t = threading.Thread(target=ytdl.download, args=([video_url], ))
            t.start()
        else:
            # Simulate a finished download
            sng.download_hook({"status": "finished"})
