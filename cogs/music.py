from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Union

import disnake
from disnake.ext.commands import command, Cog

from db import RadioDB
from db.playlist import PlaylistDB

from db.playlistSong import PlaylistSongDB
from db.song import SongDB
from models import Song
from service.music.music_ui import Music_UI
from service.music.player import Player
from utils.config_mapper import DATABASE_STATUS, MUSIC_ENABLE
from utils.distyping import Config, Context

from .commandbase import CommandBase

if TYPE_CHECKING:
    from utils.distyping import ManChanBot


class Music(CommandBase):
    def __init__(self, bot: ManChanBot):
        self.bot = bot
        self.master_player = bot.master_player

    @command()
    async def init_music1(self, ctx: Context) -> None:
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return

        radio = RadioDB.get(guild_id=ctx.guild.id)
        if radio is None:
            channel = await ctx.guild.create_text_channel(name="manchan radio")
            player_ui = await channel.send(embed=self.default_embed(), view=self.defaultView())
            RadioDB.create(ctx.guild.id, channel.id, player_ui.id)
            await ctx.send(
                f"Channel has been created: {channel.mention}, Music Player UI: [player]({player_ui.jump_url})",
                delete_after=20,
            )
            return

        music_channel = await ctx.guild.fetch_channel(radio.channel_id)
        if not isinstance(music_channel, disnake.TextChannel):
            await ctx.send("Run !resetmusic command", delete_after=5)
            return

        player_ui = await music_channel.fetch_message(radio.embed_id)
        await ctx.send(
            f"Channel already exist: {music_channel.mention}, Music Player UI already exist: [player]({player_ui.jump_url})",
            delete_after=20,
        )

    @command()
    async def reset_music1(self, ctx: Context) -> None:
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return

        radio = RadioDB.get(guild_id=ctx.guild.id)
        if radio is None:
            await ctx.send("This command is not needed", delete_after=5)
            return
        music_channel = await ctx.guild.fetch_channel(radio.channel_id)
        await music_channel.delete()

        RadioDB.delete(ctx.guild.id)
        await ctx.send(
            "Channel successfully delete and deleted from DB", delete_after=5
        )
        return

    @command(aliases=["jvc1", "music"])
    async def join_music(self, ctx: Context):
        await ctx.message.delete(delay=5)
        await self.join_music_interaction(ctx)

    @command(aliases=["lvc1"])
    async def leave_music(self, ctx: Context):
        await ctx.message.delete(delay=5)
        await self.leave_music_interaction(ctx)

    @command()
    async def play2(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return

        player = self.master_player.get_player(ctx.guild.id)
        if player is None:
            await ctx.send("Run !jvc to start", delete_after=5)
            return
        if player.get_channel_id() != ctx.channel.id:
            await ctx.send("Not in Music Channel", delete_after=5)
            return

        if args != ():
            player.add_song(" ".join(args).strip())
            player_ui = player.get_player_ui()
            if player_ui is not None:
                await player_ui.edit(
                    embed=self.edit_embed_queue(player, player_ui.embeds[0])
                )

        if player.is_paused:
            player.is_paused = False
            player.is_audio_buffered = True
            if player.voice_client is not None:
                player.voice_client.resume()
            return await ctx.send("Audio is now Resumed", delete_after=5)

        await ctx.message.delete()
        if not player.is_audio_buffered:
            await player.play_music()

    @command()
    async def add(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return

        radio = RadioDB.get(guild_id=ctx.guild.id)
        if radio is None:
            await ctx.send("Run !initmusic command", delete_after=5)
            return

        player = self.master_player.get_player(ctx.guild.id)
        if player is None:
            player = self.master_player.create_player(ctx.guild.id)

        music_channel = await ctx.guild.fetch_channel(radio.channel_id)
        if not isinstance(music_channel, disnake.TextChannel):
            await ctx.send("Run resetMusic command", delete_after=5)
            return

        player_ui = await music_channel.fetch_message(radio.embed_id)
        player.add_song(" ".join(args).strip())
        await player_ui.edit(embed=self.edit_embed_queue(player, player_ui.embeds[0]))
        await ctx.message.delete()

    @command()
    async def history(self, ctx: Context):
        await ctx.message.delete(delay=5)
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        embed = disnake.Embed()
        embed.title = "History:"
        player = self.master_player.get_player(ctx.guild.id)
        if player is None:
            return
        if not (player.get_channel_id() == ctx.channel.id):
            await ctx.send("Not in Music Channel", delete_after=5)
            return
        history_str = player.history_to_string()
        if player.is_history_empty():
            history_str = "No Songs"
        await ctx.message.delete()
        embed.add_field("", history_str)
        return await ctx.send(embed=embed, delete_after=20)

    @command()
    async def clear(self, ctx: Context):
        await ctx.message.delete(delay=5)
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        player = self.master_player.get_player(ctx.guild.id) 
        if player is None:
            return
        if not (player.get_channel_id() == ctx.channel.id):
            await ctx.send("Not in Music Channel", delete_after=5)
            return
        if player.is_connected:
            player.clear_queue()
        music_channel = await ctx.guild.fetch_channel(player.get_channel_id())
        if not isinstance(music_channel, disnake.TextChannel):
            await ctx.send("Run resetMusic command", delete_after=5)
            return
        player_ui = await music_channel.fetch_message(player.get_player_ui().id) # type: ignore
        await player_ui.edit(embed=self.edit_embed_queue(player, player_ui.embeds[0]))
        await ctx.message.delete()

    @command()
    async def skip(self, ctx: Context):
        await ctx.message.delete(delay=5)
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        player = self.master_player.get_player(ctx.guild.id)
        if player is None:
            return
        if not (player.get_channel_id() == ctx.channel.id):
            await ctx.send("Not in Music Channel", delete_after=5)
            return
        if player.is_connected:
            player.stop_player()
        await ctx.message.delete()

    @command()
    async def pause(self, ctx: Context):
        await ctx.message.delete(delay=5)
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        player = self.master_player.get_player(ctx.guild.id)
        if player is None:
            return
        if not (player.get_channel_id() == ctx.channel.id):
            await ctx.send("Not in Music Channel", delete_after=5)
            return
        if player.is_audio_buffered:
            player.is_paused = True
            player.is_audio_buffered = False
            player.voice_client.pause()  # type: ignore
            await ctx.send("Audio is now Paused", delete_after=5)
        elif player.is_paused:
            player.is_paused = False
            player.is_audio_buffered = True
            player.voice_client.resume()  # type: ignore
            await ctx.send("Audio is now Resumed", delete_after=5)
        await ctx.message.delete()

    @command(aliases=["cpl"])
    async def create_playlist(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        PlaylistDB.create(ctx.author.id, " ".join(args).strip())
        await ctx.send(
            f"Playlist: {' '.join(args).strip()} now created", delete_after=10
        )

    @command(aliases=["lpl"])
    async def list_playlist(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        playlists = PlaylistDB.get_all()
        embed = disnake.Embed()
        embed.title = "Playlists:"
        playlist_str = ""
        for playlist in playlists:
            playlist_str += str(playlist.id) + ". " + playlist.playlist_name + "\n"
        embed.add_field("", playlist_str)
        await ctx.send(embed=embed, delete_after=10)

    @command(aliases=["dpl"])
    async def delete_playlist(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        try:
            id = int(" ".join(args).strip())
        except ValueError:
            await ctx.send("Please provide a valid playlist ID (number)", delete_after=10)
            return
    
        playlist = PlaylistDB.get(id, ctx.author.id)
        if playlist is None:
            await ctx.send(
                f"Playlist: {' '.join(args).strip()} does not exist", delete_after=10
            )
            return
        PlaylistDB.delete(id)
        await ctx.send(f"Playlist: {' '.join(args).strip()} deleted", delete_after=10)

    @command(aliases=["apl"])
    async def add_playlist(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        try:
            id = int(" ".join(args).strip())
        except ValueError:
            await ctx.send("Please provide a valid playlist ID (number)", delete_after=10)
            return
        
        playlist = PlaylistDB.get_by_id(id)
        if playlist is None:
            await ctx.send(
                f"Playlist: {' '.join(args).strip()} does not exist", delete_after=10
            )
            return

        player = self.master_player.get_player(ctx.guild.id)
        if player is None:
            return
        if player.current_song is None:
            await ctx.send("No song is currently playing.", delete_after=10)
            return
        song: Song = player.current_song

        addedSong = SongDB.get_by_url(song.url)
        if addedSong is None:
            addedSong = SongDB.create(song)
        PlaylistSongDB.create(playlist.id, addedSong.id)
        await ctx.send(
            f"Song: {song.title} added to Playlist: {str(id)}", delete_after=10
        )

    @command(aliases=["aqpl"])
    async def add_queue_playlist(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        try:
            id = int(" ".join(args).strip())
        except ValueError:
            await ctx.send("Please provide a valid playlist ID (number)", delete_after=10)
            return
        
        playlist = PlaylistDB.get_by_id(id)
        if playlist is None:
            await ctx.send(
                f"Playlist: {' '.join(args).strip()} does not exist", delete_after=10
            )
            return

        player = self.master_player.get_player(ctx.guild.id)
        if player is None:
            return
        if player.current_song is None:
            await ctx.send("No song is currently playing.", delete_after=10)
            return

        for song in player.queue:
            addedSong = SongDB.get_by_url(song.url)
            if addedSong is None:
                addedSong = SongDB.create(song)
            PlaylistSongDB.create(playlist.id, addedSong.id)
        await ctx.send(f"Current Queue added to Playlist: {str(id)}", delete_after=10)

    @command(aliases=["ahqpl"])
    async def add_history_queue_playlist(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        try:
            id = int(" ".join(args).strip())
        except ValueError:
            await ctx.send("Please provide a valid playlist ID (number)", delete_after=10)
            return
        
        playlist = PlaylistDB.get_by_id(id)
        if playlist is None:
            await ctx.send(
                f"Playlist: {' '.join(args).strip()} does not exist", delete_after=10
            )
            return

        player = self.master_player.get_player(ctx.guild.id)
        if player is None:
            return
        if player.current_song is None:
            await ctx.send("No song is currently playing.", delete_after=10)
            return

        for song in player.history:
            addedSong = SongDB.get_by_url(song.url)
            if addedSong is None:
                addedSong = SongDB.create(song)
            PlaylistSongDB.create(playlist.id, addedSong.id)
        await ctx.send(
            f"Current history Queue added to Playlist: {str(id)}", delete_after=10
        )

    @command(aliases=["pls"])
    async def list_playlist_songs(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        try:
            id = int(" ".join(args).strip())
        except ValueError:
            await ctx.send("Please provide a valid playlist ID (number)", delete_after=10)
            return
        
        playlist = PlaylistSongDB.get_songs_by_playlist(id)
        if playlist is None:
            await ctx.send(
                f"Playlist: {' '.join(args).strip()} does not exist", delete_after=10
            )
            return
        embed = disnake.Embed()
        playlist_name = PlaylistDB.get_by_id(id)
        if playlist_name is None:
            return
        embed.title = playlist_name.playlist_name
        playlist_str = ""
        index = 1
        for entry in playlist:
            song = SongDB.get_by_id(entry.id)
            if song is not None:
                playlist_str += (
                    f"{index:>3}. {song.title} ({song.id})\n"
                )
            index += 1
        embed.add_field("", playlist_str)
        await ctx.send(embed=embed, delete_after=10)

    @command(aliases=["rls"])
    async def remove_playlist_song(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        try:
            playlist_id = int(args[0])
            song_id = int(args[1])
        except ValueError:
            await ctx.send("Please provide a valid playlist ID (number)", delete_after=10)
            return
        playlist = PlaylistSongDB.get_songs_by_playlist(playlist_id)
        if playlist is None:
            await ctx.send(
                f"Playlist: {' '.join(args).strip()} does not exist", delete_after=10
            )
            return
        song = SongDB.get_by_id(song_id)
        if song is None:
            await ctx.send(f"Song does not exist", delete_after=10)
            return
        PlaylistSongDB.delete_playlist_song(playlist_id, song_id)
        await ctx.send(
            f"Song {song.title} removed from Playlist: {playlist_id} deleted",
            delete_after=10,
        )

    @command(aliases=["ldpl"])
    async def load_playlist(self, ctx: Context, *args: str):
        await ctx.message.delete(delay=5)
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        try:
            id = int(" ".join(args).strip())
        except ValueError:
            await ctx.send("Please provide a valid playlist ID (number)", delete_after=10)
            return
        
        playlist = PlaylistSongDB.get_songs_by_playlist(id)
        if playlist is None:
            await ctx.send(
                f"Playlist: {' '.join(args).strip()} does not exist", delete_after=10
            )
            return
        player = self.master_player.get_player(ctx.guild.id)
        if player is None:
            return
        for entry in playlist:
            songdb = SongDB.get_by_id(entry.id)
            if songdb is not None:
                player.add_song(songdb.webpage_url)
        if player.player_ui is None:
            return
        await player.player_ui.edit(
            embed=self.edit_embed_queue(player, player.player_ui.embeds[0])
        )

    def default_embed(self) -> disnake.Embed:
        embed = disnake.Embed()
        embed.title = "MANCHAN RADIO"
        embed.description = "Please run !jvc to start radio"
        embed.add_field("Now Playing:", "Empty", inline=False)
        embed.add_field("Queue:", "Empty", inline=False)
        return embed

    def edit_embed_queue(self, player: Player, embed: disnake.Embed) -> disnake.Embed:
        embed.set_field_at(1, "Queue:", player.queue_to_string(), inline=False)
        return embed
        
    def defaultView(self) -> disnake.ui.View:
        view = disnake.ui.View()
        button = disnake.ui.Button()
        button.label = "Start VC"
        button.custom_id = "jvc"
        # button.callback = self.join_music_interaction
        view.add_item(button)
        return view
    
    async def join_music_interaction(self, ctx: Union[disnake.Interaction, Context]):
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        radio = RadioDB.get(guild_id=ctx.guild.id)
        if radio is None:
            await ctx.send("Run !initmusic command", delete_after=5)
            return
        if int(radio.channel_id) != ctx.channel.id:
            await ctx.send("Not in Music Channel", delete_after=5)
            return
        if not isinstance(ctx.author, disnake.Member) or ctx.author.voice is None:
            await ctx.send("Connect to a voice channel!", delete_after=5)
            return
        player = self.master_player.create_player(ctx.guild.id)
        player.set_channel_id(int(radio.channel_id))
        music_channel = await ctx.guild.fetch_channel(player.get_channel_id())
        if isinstance(music_channel, disnake.TextChannel):
            player_ui = await music_channel.fetch_message(radio.embed_id)
            player.channel_id = int(radio.channel_id)
            player.player_ui = player_ui
            embed = self.default_embed()
            embed.description = "Please run !lvc to stop radio"
            await player_ui.edit(embed=embed, view= Music_UI.main_View())
        if not self.is_connected and ctx.author.voice.channel is not None:
            self.voice_client = await ctx.author.voice.channel.connect() 
            self.is_connected = True
            await ctx.send("Connected", delete_after=5)

    async def leave_music_interaction(self, ctx: Union[disnake.Interaction, Context]):
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return

        voice_client = ctx.guild.voice_client
        if voice_client is not None:
            await voice_client.disconnect(force=False)

        player = self.master_player.get_player(ctx.guild.id)
        if player is not None:
            music_channel = await ctx.guild.fetch_channel(player.get_channel_id())
            self.master_player.destory_player(ctx.guild.id)
            if (
                isinstance(music_channel, disnake.TextChannel)
                and player.player_ui is not None
            ):
                await player.player_ui.edit(embed=self.default_embed(), view=self.defaultView())
        await ctx.send("Bot left VC and player instance destroyed", delete_after=5)

    async def play_music_interaction(self, ctx: Union[disnake.Interaction, Context]):
        if ctx.guild is None:
            return

        player = self.master_player.get_player(ctx.guild.id)
        if player is None:
            return
        if player.is_paused:
            player.is_paused = False
            player.is_audio_buffered = True
            if player.voice_client is not None:
                player.voice_client.resume()
            return
        if not player.is_audio_buffered:
            await player.play_music()

    async def list_playlist_interaction(self, ctx: disnake.Interaction):
        await ctx.send(view=Music_UI.playlist_view())

    # def main_View(self) -> disnake.ui.View:
    #     view = disnake.ui.View()
    #     play_button = disnake.ui.Button()
    #     play_button.label = "Play"
    #     play_button.custom_id = "play"
    #     # play_button.callback = self.play_music_interaction

    #     skip_button = disnake.ui.Button()
    #     skip_button.label = "Skip"
    #     # skip_button.callback = self.skip_callback

    #     add_button = disnake.ui.Button()
    #     add_button.label = "Add to Playlist"
    #     # add_button.callback = self.add_callback

    #     leave_button = disnake.ui.Button()
    #     leave_button.label = "Leave VC"
    #     leave_button.custom_id = "leave"
    #     # leave_button.callback = self.leave_music_interaction

    #     view.add_item(play_button)
    #     view.add_item(skip_button)
    #     view.add_item(add_button)
    #     view.add_item(leave_button)
    #     return view
    
    @Cog.listener(disnake.Event.button_click)
    async def help_listener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id not in ["play", "leave", "jvc", "add"]:
            # We filter out any other button presses except
            # the components we wish to process.
            return
        
        # if inter.component.custom_id == "add":
        #     await self.list_playlist_interaction(inter)

        # player = self.master_player.get_player(inter.guild.id)
        # if player is None:
        #     return
        
        await inter.response.defer()

        if inter.component.custom_id == "play":
            await self.play_music_interaction(inter)
        elif inter.component.custom_id == "leave":
            await self.leave_music_interaction(inter)
        elif inter.component.custom_id == "jvc":
            await self.join_music_interaction(inter)
        elif inter.component.custom_id == "add":
            await self.list_playlist_interaction(inter)

    @command()
    async def testButton(self, ctx: Context):
        await ctx.send(view= Music_UI.main_View())
        return


    @classmethod
    def is_enabled(cls, configs: Config = {}) :
        return (configs.get(MUSIC_ENABLE) and configs.get(DATABASE_STATUS))


def setup(bot: ManChanBot):
    if Music.is_enabled(bot.configs):
        bot.add_cog(Music(bot))  # type: ignore
    else:
        logging.warning("SKIPPING: cogs.Music")

#   File "D:\dev\man-chan\venv\lib\site-packages\disnake\client.py", line 703, in _run_event
#     await coro(*args, **kwargs)
#   File "D:\dev\man-chan\cogs\music.py", line 550, in help_listener
#     await self.join_music_interaction(inter)
#   File "D:\dev\man-chan\cogs\music.py", line 469, in join_music_interaction
#     if not self.is_connected and ctx.author.voice.channel is not None:
# AttributeError: 'Music' object has no attribute 'is_connected'