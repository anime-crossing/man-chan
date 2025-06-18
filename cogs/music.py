from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import disnake
from disnake.ext.commands import Cog, slash_command

from service.music.music_interactions import Music_Interactions, PlaylistAddType

from utils.config_mapper import DATABASE_STATUS, MUSIC_ENABLE
from utils.distyping import Config

from .commandbase import CommandBase

if TYPE_CHECKING:
    from utils.distyping import ManChanBot


class Music(CommandBase):
    def __init__(self, bot: ManChanBot):
        self.bot = bot
        self.master_player = bot.master_player

    @slash_command(description="Initializations the music channel")
    async def init_music(self, inter: disnake.ApplicationCommandInteraction):
        await Music_Interactions.init_music_interaction(inter)

    @slash_command(description="Deletes the music channel")
    async def reset_music(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await Music_Interactions.reset_music(inter)

    @slash_command(description="Adds the bot to VC to start playing music")
    async def join_music(self, inter: disnake.ApplicationCommandInteraction):
        await Music_Interactions.join_music_interaction(inter)

    @slash_command(description="Stops the bot and leaves in VC")
    async def leave_music(self, inter: disnake.ApplicationCommandInteraction):
        await Music_Interactions.leave_music_interaction(inter)

    @slash_command(description="Unpauses player or starts playing queue/provided song")
    async def play(self, inter: disnake.ApplicationCommandInteraction, song: str = ""):
        await Music_Interactions.play_interaction(inter, song)

    @slash_command(description="Adds song to the queue")
    async def add(self, inter: disnake.ApplicationCommandInteraction, song: str):
        await Music_Interactions.add_interaction(inter, song)

    @slash_command(description="Shows session history")
    async def history(self, inter: disnake.ApplicationCommandInteraction):
        await Music_Interactions.history_interaction(inter)

    @slash_command(description="Clears the queue")
    async def clear(self, inter: disnake.ApplicationCommandInteraction):
        await Music_Interactions.clear_interaction(inter)

    @slash_command(description="Skips the current song")
    async def skip(self, inter: disnake.ApplicationCommandInteraction):
        await Music_Interactions.skip_interaction(inter)

    @slash_command(description="Pause the current song")
    async def pause(self, inter: disnake.ApplicationCommandInteraction):
        await Music_Interactions.pause_interaction(inter)

    @slash_command(description="Creates a playlist")
    async def create_playlist(self, inter: disnake.ApplicationCommandInteraction, playlist_name: str):
        await Music_Interactions.create_playlist_interaction(inter, playlist_name)

    @slash_command(description="List all playlists")
    async def list_playlist(self, inter: disnake.ApplicationCommandInteraction):
        await Music_Interactions.list_playlist_interaction(inter)

    @slash_command(description="Deletes a playlist")
    async def delete_playlist(self, inter: disnake.ApplicationCommandInteraction, playlist_id: int):
        await Music_Interactions.delete_playlist_interaction(inter, playlist_id)

    @slash_command(description="Add song(s) to playlist")
    async def add_playlist(self, inter: disnake.ApplicationCommandInteraction, playlist_id: int, add_type: PlaylistAddType):
        await Music_Interactions.add_playlist_interaction(inter, playlist_id, PlaylistAddType(add_type))

    @slash_command(description="List songs in Playlist")
    async def list_playlist_songs(self, inter: disnake.ApplicationCommandInteraction, playlist_id: int):
        await Music_Interactions.list_playlist_songs_interaction(inter, playlist_id)

    @slash_command(description="Remove Song from Playlist")
    async def remove_playlist_song(self, inter: disnake.ApplicationCommandInteraction, playlist_id: int, song_id: int):
        await Music_Interactions.remove_playlist_song(inter, playlist_id, song_id)

    @slash_command(description="Add Playlist to queue")
    async def load_playlist(self, inter: disnake.ApplicationCommandInteraction, playlist_id: int):
        await Music_Interactions.load_playlist_interaction(inter, playlist_id)
  
    @Cog.listener(disnake.Event.button_click)
    async def help_listener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id not in ["jvc"]:
            return 
        await Music_Interactions.join_music_interaction(inter)

    @classmethod
    def is_enabled(cls, configs: Config = {}) :
        return (configs.get(MUSIC_ENABLE) and configs.get(DATABASE_STATUS))

def setup(bot: ManChanBot):
    if Music.is_enabled(bot.configs):
        bot.add_cog(Music(bot))  # type: ignore
    else:
        logging.warning("SKIPPING: cogs.Music")
