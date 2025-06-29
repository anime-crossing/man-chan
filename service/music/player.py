import logging
from typing import Optional

import disnake
from disnake import Message, VoiceClient
from models import Song

from .queue import Queue


class Player:
    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    def __init__(self) -> None:
        self._queue: Queue = Queue()
        self.channel_id: int = 0
        self.player_ui: Optional[Message] = None
        self.voice_client: Optional[VoiceClient] = None
        self.is_paused: bool = False
        self.is_connected: bool = False
        self.is_audio_buffered: bool = False
        self.current_song: Optional[Song] = None
        self.loop: bool = False

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

    def get_player_ui(self) -> Optional[Message]:
        return self.player_ui

    async def set_voice_client(self, inter : disnake.Interaction):
        if not isinstance(inter.author, disnake.Member) or inter.author.voice is None:
            await inter.send("Connect to a voice channel!", delete_after=5)
            return
        if not self.is_connected and inter.author.voice.channel is not None:
            self.voice_client = await inter.author.voice.channel.connect() 
            self.is_connected = True
            await inter.send("Connected", delete_after=5)

    async def play_music(self):
        if (not self._queue.is_queue_empty()) or self.loop:
            self.is_audio_buffered = True

            if not self.loop:
                self.current_song = self.queue[0]
                self.remove_song()
            player_ui = self.get_player_ui()
            if player_ui is not None:
                await player_ui.edit(embed=self.edit_embed())
            source = disnake.FFmpegPCMAudio(self.current_song.url, **self.FFMPEG_OPTIONS)  # type: ignore

            def after(error):  # type: ignore
                if error:
                    logging.warning(f"Playback error: {error}")
                else:
                    self.voice_client.loop.create_task(self.play_music())  # type: ignore

            self.voice_client.play(source, after=after)  # type: ignore
        else:
            self.is_audio_buffered = False
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

    def edit_embed(self) -> disnake.Embed:
        embed = disnake.Embed()
        embed.title = "MANCHAN RADIO"
        embed.description = "Please run !lvc to stop radio"
        embed.add_field("Paused:", str(self.is_paused))
        embed.add_field("Loop:", str(self.loop))
        embed.add_field("Now Playing:", self.current_song.title if self.current_song else "Empty", inline=False)
        embed.add_field("Queue:", self.queue_to_string(), inline=False)
        embed.set_image(None)
        if self.current_song:
            embed.set_image(self.current_song.thumbnail_url) 
        return embed
