from disnake import Message
import disnake
from .queue import Queue

class Player:

    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    def __init__(self) -> None:
        self.queue = Queue()
        self.channel_id = None
        self.player_ui = None
        self.voice_client = None
        self.is_paused = False
        self.is_connected = False
        self.is_playing = False

        self.current_song = None

    def set_channel_id(self, id: int):
        self.channel_id = id

    def get_channel_id(self):
        return self.channel_id
    
    def set_player_ui(self, player_ui: Message):
        self.player_ui = player_ui

    def play_music(self):
        if not self.queue.is_empty():
            self.is_playing = True

            url = self.queue.queue[0]['url']
            self.current_song = self.queue.queue[0]
            self.queue.remove_song()
            source = disnake.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS)
            self.voice_client.play(source, after= lambda e: self.play_music()) # type: ignore
        else: 
            self.is_playing = False
            self.current_song = []

    def leave_voice(self):
        self.is_playing = False
        self.is_paused = False
        self.is_connected = False
        self.voice_client = None
        self.queue.queue = []
        self.queue.session_queue = []
        self.current_song = []

    def clear_queue(self):
        self.queue.queue.clear()

    def stop_player(self):
        self.current_song = []
        self.voice_client.stop()

    def get_status(self):
        status = ''
        status += status + "Connected: " + str(self.is_connected) + '\n'
        status += status + "Playing: " + str(self.is_playing) + '\n'
        status += status + "Paused: " + str(self.is_paused) + '\n'
        return status

