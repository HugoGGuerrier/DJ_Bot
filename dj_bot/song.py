from dj_bot import LOGGER_NAME

import logging
import discord


class Song:
    """
    Song class.

    This class contains all information about a playable song
    """

    # ----- Constructor -----

    def __init__(self, title: str, video_id: str, duration: str, ready_func=None):
        """
        Create a new song with all its parameters

        params :
            - title: str = The song youtube title
            - video_id: str = The song video id
            - duration: str = The song duration in a string
            - ready_func = The function to call when the song will be ready
        """

        # Assign the attributes
        self.title: str = title
        self.video_id: str = video_id
        self.duration: str = duration
        self.is_ready: bool = False
        self.ready_func = ready_func

    # ----- Class methods -----

    def __str__(self) -> str:
        """
        Get the string representation of a song

        return -> str = The string
        """

        res: str = self.title + " [" + self.duration + "]"
        if self.is_ready:
            res += " Ready"
        else:
            res += " Downloading..."
        return res

    def download_hook(self, s) -> None:
        """
        The function to call during the song downloading

        params :
            - s: dict = The download informations
        """

        if s["status"] == "finished":
            # Set the state to ready
            self.is_ready = True

            # Call the callback function
            if self.ready_func is not None:
                self.ready_func(self)

            # Log the song downloading
            logging.getLogger(LOGGER_NAME).info("Song " + self.title + " - " + self.video_id + " has been downloaded")

    def get_audio_source(self, os_model: str) -> discord.AudioSource:
        """
        Get the song audio source to play it in discord

        params :
            - os_model: str = The model of the current os
        """

        source_file = ".songs/" + self.video_id + ".mp4"
        return discord.FFmpegPCMAudio(source=source_file, executable="./dj_bot/ffmpeg/ffmpeg_" + os_model)
