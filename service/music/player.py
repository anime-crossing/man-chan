from typing import Optional

import disnake
from disnake import Embed, Message, VoiceClient

from models import Song

from .queue import Queue


class Player:

    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    def __init__(self) -> None:
        self._queue: Queue = Queue()
        self.channel_id: Optional[int] = None
        self.player_ui: Optional[Message] = None
        self.voice_client: Optional[VoiceClient] = None
        self.is_paused: bool = False
        self.is_connected: bool = False
        self.is_audio_buffered: bool = False
        self.current_song: Optional[Song] = None
        self.embed: Embed = disnake.Embed(title="MANCHAN MUSIC BOT")

    @property
    def queue(self) -> list[Song]:
        return self._queue.queue

    @property
    def history(self) -> list[Song]:
        return self._queue.session_history

    def add_song(self, song_name: str):
        self._queue.add_song(song_name)

    def remove_song(self):
        self._queue.remove_song()

    def is_queue_empty(self) -> bool:
        return self._queue.is_queue_empty()

    def is_history_empty(self) -> bool:
        return self._queue.is_history_empty()

    def queue_to_string(self) -> str:
        return self._queue.queue_to_string()

    def history_to_string(self) -> str:
        return self._queue.history_to_string()

    def set_channel_id(self, id: int):
        self.channel_id = id

    def get_channel_id(self):
        return self.channel_id

    def set_player_ui(self, player_ui: Message):
        self.player_ui = player_ui

    async def set_voice_client(self, ctx): # type: ignore
        if ctx.author.voice is None:  # type: ignore
            return await ctx.send("Connect to a voice channel!", delete_after=5)
        if not self.is_connected:
            self.voice_client = await ctx.author.voice.channel.connect()  # type: ignore
            await ctx.send("Connected", delete_after=5)
            self.is_connected = True

    def play_music(self):
        if not self._queue.is_queue_empty():
            self.is_audio_buffered = True

            url = self.queue[0].url
            self.current_song = self.queue[0]
            self.remove_song()
            source = disnake.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS) # type: ignore
            self.voice_client.play(source, after=lambda e: self.play_music())  # type: ignore
        else:
            self.is_audio_buffered = False
            self.current_song = None

    def leave_voice(self):
        self.is_audio_buffered = False
        self.is_paused = False
        self.is_connected = False
        self.voice_client = None
        self.queue.clear()
        self.history.clear()
        self.current_song = None

    def clear_queue(self):
        self.queue.clear()

    def stop_player(self):
        self.current_song = None
        self.is_paused = False
        self.voice_client.stop()  # type: ignore

    def get_status(self):
        status = ""
        status += "Connected: " + str(self.is_connected) + "\n"
        status += "Playing: " + str(self.is_audio_buffered) + "\n"
        status += "Paused: " + str(self.is_paused) + "\n"
        return status
