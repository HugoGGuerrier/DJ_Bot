from dj_bot import LOGGER_NAME, FFMPEG_DIR, DOWNLOAD_DIR

import logging
import discord
import json


class Song:
    """
    Song class.

    This class contains all information about a playable song
    """

    # ----- Constructor -----

    def __init__(self, title: str, video_id: str, duration: str):
        """
        Create a new song with all its parameters

        params :
            - title: str = The song youtube title
            - video_id: str = The song video id
            - duration: str = The song duration in a string
            - ready_func = The function to call when the song will be ready to be played
        """

        # Assign the attributes
        self.title: str = title
        self.video_id: str = video_id
        self.duration: str = duration
        self.is_ready: bool = False
        self.ready_func = None

    # ----- Serialization -----

    def serialize(self) -> str:
        """
        Serialize the song in a json string

        return -> str = The json string of the song
        """

        # Create the dict to create the json
        song_dict: dict = {
            "title": self.title,
            "video_id": self.video_id,
            "duration": self.duration
        }

        # Return the json string
        return json.dumps(song_dict)

    @classmethod
    def deserialize(cls, src: str):
        """
        Return a Song with the serialized string

        params :
            - src: str = The json string
        """

        # Load the dict from the string
        song_dict = json.loads(src)

        # Return a new song with the parameters
        return cls(song_dict["title"], song_dict["video_id"], song_dict["duration"])

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

            # Log the song downloading success
            logging.getLogger(LOGGER_NAME).info("Song " + self.title + " - " + self.video_id + " has been downloaded")

            # Call the callback function
            if self.ready_func is not None:
                self.ready_func(self)

    def get_audio_source(self) -> discord.AudioSource:
        """
        Get the song audio source to play it in discord
        """

        source_file = DOWNLOAD_DIR + self.video_id + ".mp4"
        return discord.FFmpegPCMAudio(source=source_file, executable=FFMPEG_DIR + "ffmpeg")
