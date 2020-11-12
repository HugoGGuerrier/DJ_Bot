from dj_bot import clients
from dj_bot import song

import queue

# ----- DJBot states -----

STOP_STATE: int = 0
PLAY_STATE: int = 1

# This class handle all the bot needs to know
class DJBot:

    # ----- Constructor -----

    # Create a new DJ Bot
    def __init__(
            self,
            discord_token: str,
            youtube_token: str,
            request_channel: str,
            admin_users: list,
            admin_roles: list,
            queue_max_size: int
    ):

        # Assign the attributes
        self.discord_token: str = discord_token
        self.youtube_token: str = youtube_token
        self.req_channel: str = request_channel
        self.admin_users: list = admin_users
        self.admin_roles: list = admin_roles
        self.queue_max_size = queue_max_size

        self.state: int = STOP_STATE
        self.music_queue: queue.Queue = queue.Queue(self.queue_max_size)

        self.discord_client: clients.DJDiscordClient = clients.DJDiscordClient(self, self.req_channel,
                                                                               self.admin_users, self.admin_roles)
        self.youtube_client: clients.DJYoutubeClient = clients.DJYoutubeClient(self, self.youtube_token)

    # ----- Class methods -----

    # --- Music manipulation methods

    # Add a music and catch the exception if the queue is full
    def add_music(self, sng: song.Song) -> None:
        try:
            self.music_queue.put_nowait(sng)
        except queue.Full as _:
            self.send_error_message("Cannot add a song, the queue is full  :disappointed_relieved:")

    # Play the next music in the queue TODO
    def play_music(self) -> None:
        self.state = PLAY_STATE
        pass

    # Choose the search result TODO
    def choose_search(self, song_id: str):
        pass

    # Stop the music playing TODO
    def stop_music(self) -> None:
        self.state = STOP_STATE
        pass

    # Empty the queue
    def empty_queue(self) -> None:
        self.music_queue = queue.Queue(self.queue_max_size)

    # --- Interaction methods

    # Show the bot help
    def show_help(self) -> None:
        help_message: str = "Hello, I'm the DJ bot (Discord Jukebox Bot)," \
                            " you can ask me to play music from youtube  :slight_smile:\n"
        help_message += "```\n"
        help_message += "Use these commands :\n"
        help_message += " !help : Display this help message\n"
        help_message += " !play <SONG> : Add the song to the playing queue\n"
        help_message += " !stop : Stop my music playing\n"
        help_message += " !search <SONG> : List songs on youtube\n"
        help_message += " !choose <ID> : Choose a search result\n"
        help_message += " !queue : Display playing queue\n"
        help_message += " !empty-queue : Empty the music queue (Admin)\n"
        help_message += " !shutdown : Stop me :'( (Admin)\n\n"
        help_message += "```"
        self.send_message(help_message)

    # Show the queue state in a discord message
    def show_queue(self) -> None:
        queue_message: str

        if self.music_queue.qsize() > 0:
            queue_message = "Current queue :\n"
            queue_message += "```\n"

            # Iterate over the queue
            new_queue = queue.Queue(self.queue_max_size)
            for i in range(self.music_queue.qsize()):
                item = self.music_queue.get_nowait()
                queue_message += str(i + 1) + ". "
                queue_message += item.title + "\n"
                new_queue.put_nowait(item)

            self.music_queue = new_queue

            queue_message += "```"
        else:
            queue_message = "Current queue is empty..."

        self.send_message(queue_message)

    # Display the youtube search for the keyword
    def show_search(self, search_q: str) -> None:
        print(self.youtube_client.search_videos(search_q, 10))
        pass

    # Send a message to the listen channel
    def send_message(self, message: str) -> None:
        self.discord_client.loop.create_task(self.discord_client.send_message(message))

    # Send an error message to the users
    def send_error_message(self, error: str) -> None:
        final_message = "**ERROR** : " + error
        self.send_message(final_message)

    # --- Bot control methods

    # Start the bot
    def start(self) -> None:
        self.discord_client.run(self.discord_token)

    # Stop the bot from running
    def stop(self) -> None:
        self.discord_client.loop.create_task(self.discord_client.logout())
        self.discord_client.loop.create_task(self.discord_client.close())
