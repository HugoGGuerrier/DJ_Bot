from dj_bot import clients, song, utils
from dj_bot import DOWNLOAD_DIR, CACHE_FILE, SAVE_FILE, LOGGER_NAME

import discord
import json
import os
import logging

# ----- DJBot states -----

PAUSE_STATE: int = 0
PLAY_STATE: int = 1
IDLE_STATE: int = 2


class DJBot:
    """
    DJBot class.

    This class is the main class of the bot, it contains all methods to control the music playing
    """

    # ----- Constructor -----

    def __init__(
            self,
            discord_token: str,
            youtube_token: str,
            request_channel: str,
            playing_channel: str,
            admin_users: list,
            admin_roles: list,
            queue_max_size: int,
            max_result: int,
            remove_req: bool
    ):
        """
        Create a new bot with the wanted parameters
        """

        # Assign the attributes
        self.discord_token: str = discord_token
        self.youtube_token: str = youtube_token
        self.req_channel: str = request_channel
        self.play_channel: str = playing_channel
        self.admin_users: list = admin_users
        self.admin_roles: list = admin_roles
        self.queue_max_size = queue_max_size
        self.max_result: int = max_result
        self.remove_req: bool = remove_req

        self.state: int = IDLE_STATE
        self.song_queue: list = list()
        self.current_song: song.Song = None
        self.user_search: dict = dict()

        self.discord_client: clients.DJDiscordClient = clients.DJDiscordClient(self, self.req_channel, self.play_channel, self.remove_req)
        self.youtube_client: clients.DJYoutubeClient = clients.DJYoutubeClient(self, self.youtube_token)

    # ----- Class methods -----

    # --- Internal methods

    def is_admin(self, user: discord.Member) -> bool:
        """
        Verify is an user is a bot admin

        params :
            - user: discord.Member = A discord Member

        return -> bool = True if the user is an admin, False else
        """

        # Get the real user name
        user_name: str = utils.get_user_fullname(user)

        # Verify the roles
        for role in user.roles:
            if role.name in self.admin_roles:
                return True

        # Verify the name
        if user_name in self.admin_users:
            return True

        # Return the default response
        return False

    def add_song(self, sng: song.Song, feedback=True) -> None:
        """
        Add a song to the current queue with size verification adn download it

        params :
            - sng: dj_bot.song.Song = A song you want to add to the queue
        """

        if len(self.song_queue) < self.queue_max_size:
            sng.ready_func = self.song_is_ready
            self.song_queue.append(sng)
            self.youtube_client.download_song(sng)
            if feedback:
                self.send_message("**" + sng.user + "** add the song **" + sng.title + "** to the queue  :smile:")
        else:
            if feedback:
                self.send_error_message("Sorry **" + sng.user + "**, but the queue is full  :disappointed_relieved:")

    def song_is_ready(self, sng: song.Song) -> None:
        """
        Function to call when a song is downloaded

        param :
            - sng : song.Song = The song that is ready
        """

        if sng.video_id == self.song_queue[0].video_id and self.state == IDLE_STATE:
            self.current_song = self.song_queue.pop(0)
            self.play_music()

    def next_in_queue(self, _) -> None:
        """
        Play the next song in the queue

        params :
            - _ = An unused parameter to avoid errors with the callback
        """

        # Stop the current song to make sure
        self.discord_client.stop_song()
        self.current_song = None

        # Play the next song if it exists
        if len(self.song_queue) > 0 and self.song_queue[0].is_ready:
            self.current_song = self.song_queue.pop(0)
            self.discord_client.play_song(self.current_song)
        else:
            self.state = IDLE_STATE

    # --- Music manipulation methods

    def add_music(self, title: str, user: discord.Member) -> None:
        """
        Method call by the discord client when a user add a music with the !play command

        params :
            - title: str = The title of the music to add
        """

        # Get the song dict by calling the youtube client
        song_dict: dict = self.youtube_client.get_first_video(title)

        # Create and add the song instance
        sng: song.Song = song.Song(song_dict["title"], song_dict["id"], song_dict["duration"], user.display_name)
        self.add_song(sng)

    def choose_search(self, choose_id: str, user: discord.Member) -> None:
        """
        Choose a search result after an user made a search

        params :
            - choose_id: str = The id of the search option
            - user: discord.Member = The user who made the choice
        """

        # Get the user search list or None
        user_name = utils.get_user_fullname(user)
        user_search = self.user_search.get(user_name, None)

        # If the user made a research provide a result, else send an error message
        if user_search is not None:
            if choose_id != "":
                try:
                    # Get the correct song dict and create the song instance
                    song_dict: dict = user_search[int(choose_id) - 1]
                    sng: song.Song = song.Song(song_dict["title"], song_dict["id"], song_dict["duration"], user.display_name)
                    self.add_song(sng)

                    # Erase the user search
                    self.user_search[user_name] = None
                except ValueError as _:
                    self.send_message("Id must be an integer  :angry:")
                except IndexError as _:
                    self.send_message("Choose an id between 0 and " + str(len(user_search) - 1) + " (you stupid)")
            else:
                self.send_message("Choose an id between 0 and " + str(len(user_search) - 1) + " (you stupid)")
        else:
            self.send_message("Perform a **_!search_** before choosing an id  :slight_smile:")

    def play_music(self) -> None:
        """
        Start the music playing if it's not the case
        """

        if self.state != PLAY_STATE:
            self.state = PLAY_STATE
            self.discord_client.play_song(self.current_song)

    def skip_music(self):
        """
        Skip the current playing music
        """

        self.discord_client.stop_song()

    def pause_music(self) -> None:
        """
        Pause the music playing
        """

        if self.state == PLAY_STATE:
            self.state = PAUSE_STATE
            self.discord_client.pause_song()

    def resume_music(self) -> None:
        """
        Resume the previously playing music
        """

        if self.state == PAUSE_STATE:
            self.state = PLAY_STATE
            self.discord_client.resume_song()

    def empty_queue(self, user: discord.Member) -> None:
        """
        Empty the current music queue

        params :
            - user: discord.Member = The user who made the request
        """

        # Verify that the user is an admin
        if self.is_admin(user):
            self.song_queue.clear()
            self.send_message("Queue has been cleaned  :thumbsup:")
        else:
            self.send_message("You are not an admin  :middle_finger:")

    # --- Interaction methods

    def show_help(self) -> None:
        """
        Send a message to help users understand commands
        """

        # Prepare the help message
        help_message: str = "Hello, I'm the DJ bot (Discord Jukebox Bot)," \
                            " you can ask me to play music from youtube  :slight_smile:\n"
        help_message += "Use these commands to order me :\n"
        help_message += "```\n"
        help_message += "!help (!h) : Display this help message\n"
        help_message += "!play (!pl) <SONG> : Add the song to the playing queue\n"
        help_message += "!skip (!sk) : Skip the current song\n"
        help_message += "!pause (!pa) : Pause my music playing\n"
        help_message += "!resume (!re) : Resume the previously paused music\n"
        help_message += "!search (!se) <SONG> : List songs on youtube\n"
        help_message += "!choose (!ch) <ID> : Choose a search result\n"
        help_message += "!current (!cu) : Display the current song"
        help_message += "!queue (!qu) : Display playing queue\n"
        help_message += "!empty-queue : Empty the music queue (Admin)\n"
        help_message += "!clean-cache : Clean the song cache (Admin)\n"
        help_message += "!shutdown : Stop me :'( (Admin)\n"
        help_message += "```"

        # Send the help message
        self.send_message(help_message)

    def show_current(self) -> None:
        """
        Show the music that is currently playing if exists
        """

        if self.current_song is not None:
            self.send_message("Current song is :```" + self.current_song.title + "```")
        else:
            self.send_message("There is no current song...")

    def show_queue(self) -> None:
        """
        Send a message with the current queue
        """

        # Prepare the queue message
        queue_message: str

        if len(self.song_queue) > 0:
            queue_message = "Current queue :\n"
            queue_message += "```\n"

            # Iterate over the queue
            for i in range(len(self.song_queue)):
                queue_message += str(i + 1) + ". " + str(self.song_queue[i]) + "\n"

            queue_message += "```"
        else:
            queue_message = "Current queue is empty..."

        # Send the queue message
        self.send_message(queue_message)

    def show_search(self, search_q: str, user: discord.Member) -> None:
        """
        Send a message with the result of the research for a keyword

        params :
            - search_q: str = The search keyword
            - user: discord.Member = The user who made the research
        """

        # Get the search result from the client
        search_result: list = self.youtube_client.search_videos(search_q, self.max_result)

        # Store the user search
        user_name = user.name + "#" + user.discriminator
        self.user_search[user_name] = search_result

        # Create the search message
        search_message: str = user.display_name + " here is the result for \"" + search_q + "\" :\n"
        search_message += "```\n"
        for i in range(len(search_result)):
            search_message += str(i + 1) + ". "
            search_message += search_result[i]["title"] + " - " + search_result[i]["channel_title"]
            search_message += " [" + search_result[i]["duration"] + "]\n"
        search_message += "```"
        search_message += "Type **_!choose <ID>_** to add a song to the queue"

        # Send the message
        self.send_message(search_message)

    def send_message(self, message: str) -> None:
        """
        Send a message to the listened channel

        params :
            - message: str = The message you want to send
        """

        self.discord_client.send_message(message)

    def send_error_message(self, error: str) -> None:
        """
        Send an error message to the listened channel

        params :
            - error: str = The error message to send
        """

        # Format and send the message
        final_message = "**ERROR** : " + error
        self.send_message(final_message)

    # --- Bot control methods

    def save(self) -> None:
        """
        Save the current bot state in a file to load it the next time
        """

        # Create the export dict
        res_dict: dict = {
            "current": None,
            "queue": list()
        }

        # Create the current song string
        if self.current_song is not None:
            res_dict["current"] = self.current_song.serialize()

        # Fill the queue in the export dict
        for sng in self.song_queue:
            res_dict["queue"].append(sng.serialize())

        # Open the save file
        save_file = open(SAVE_FILE, mode="w")
        save_file.write(json.dumps(res_dict))
        save_file.close()

    def load(self) -> None:
        """
        Load the bot state from the save file
        """

        # Open and read the save file
        try:
            save_file = open(SAVE_FILE, mode="r")
            save_dict = json.loads(save_file.read())
            save_file.close()

            # Reload the current song
            if save_dict["current"] is not None:
                self.add_song(song.Song.deserialize(save_dict["current"]), False)

            # Reload the queue
            for sng_str in save_dict["queue"]:
                self.add_song(song.Song.deserialize(sng_str), False)
        except FileNotFoundError as _:
            logging.getLogger(LOGGER_NAME).info("Save file not found, one will be created")

    def clean_song_files(self) -> None:
        """
        Erase all song files except those that are needed
        """

        for filename, dirs, files in os.walk(DOWNLOAD_DIR):
            for file in files:
                rm = True
                for sng in self.song_queue:
                    if sng.video_id + ".mp4" == file:
                        rm = False
                if self.current_song is not None:
                    if self.current_song.video_id + ".mp4" == file:
                        rm = False
                if rm:
                    os.remove(DOWNLOAD_DIR + file)

    def clean_song_cache(self, user: discord.Member) -> None:
        """
        Clean the current song cache

        params :
            - user: discord.Member = The user who made the request
        """

        # Verify that the user is an admin
        if self.is_admin(user):
            try:
                os.remove(CACHE_FILE)
            except FileNotFoundError as _:
                pass
            self.clean_song_files()
            self.send_message("Song cache has been cleaned  :thumbsup:")
        else:
            self.send_message("You are not an admin  :middle_finger:")

    def start(self) -> None:
        """
        Start the bot
        """

        self.discord_client.run(self.discord_token)

    def shutdown(self, user: discord.Member) -> None:
        """
        Method called by the discord client to shutdown the bot

        params :
            - user: discord.Member = The user who made the request
        """

        # Verify that the user is an admin
        if self.is_admin(user):
            self.save()
            self.stop()
        else:
            self.send_message("You are not an admin  :middle_finger:")

    def stop(self) -> None:
        """
        Stop the bot
        """

        self.discord_client.disconnect()
        self.discord_client.loop.create_task(self.discord_client.logout())
        self.discord_client.loop.create_task(self.discord_client.close())
