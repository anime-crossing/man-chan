from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict

import disnake
from disnake.ext.commands import command

from db import RadioDB
from db.playlist import PlaylistDB

from db.playlistSong import PlaylistSongDB
from db.song import SongDB
from models import Song
from service.music.player import Player
from utils.distyping import Context

from .commandbase import CommandBase

if TYPE_CHECKING:
    from utils.distyping import ManChanBot


class Music(CommandBase):
    def __init__(self, bot: ManChanBot):
        self.bot = bot
        self.master_player = bot.master_player

    @command()
    async def init_music(self, ctx: Context) -> None:
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return

        radio = RadioDB.get(guild_id=ctx.guild.id)
        if radio is None:
            channel = await ctx.guild.create_text_channel(name="manchan radio")
            player_ui = await channel.send(embed=self.default_embed())
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
    async def reset_music(self, ctx: Context) -> None:
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

    @command(aliases=["jvc"])
    async def join_music(self, ctx: Context):
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        radio = RadioDB.get(guild_id=ctx.guild.id)
        if radio is None:
            await ctx.send("Run !initmusic command", delete_after=5)
            return
        player = self.master_player.create_player(ctx.guild.id)
        player.set_channel_id(radio.channel_id)
        music_channel = await ctx.guild.fetch_channel(player.get_channel_id())
        if isinstance(music_channel, disnake.TextChannel):
            player_ui = await music_channel.fetch_message(radio.embed_id)
            player.channel_id = int(radio.channel_id)
            player.player_ui = player_ui
            embed = self.default_embed()
            embed.description = ""
            await player_ui.edit(embed=embed)
        await player.set_voice_client(ctx)

    @command(aliases=["lvc"])
    async def leave_music(self, ctx: Context):
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return

        voice_client = ctx.voice_client
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
                await player.player_ui.edit(embed=self.default_embed())
        await ctx.send("Bot left VC and player instance destroyed", delete_after=5)

    @command()
    async def play(self, ctx: Context, *args: str):
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
        PlaylistDB.create(ctx.author.id, " ".join(args).strip())
        await ctx.send(
            f"Playlist: {' '.join(args).strip()} now created", delete_after=10
        )

    @command(aliases=["lpl"])
    async def list_playlist(self, ctx: Context, *args: str):
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
        id = int(" ".join(args).strip())
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
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        id = int(" ".join(args).strip())
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
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        id = int(" ".join(args).strip())
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
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        id = int(" ".join(args).strip())
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
        id = int(" ".join(args).strip())
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
                    str(index) + ". " + song.title + "(" + str(song.id) + ")" + "\n"
                )
            index += 1
        embed.add_field("", playlist_str)
        await ctx.send(embed=embed, delete_after=10)

    @command(aliases=["rls"])
    async def remove_playlist_song(self, ctx: Context, *args: str):
        playlist_id = int(args[0])
        song_id = int(args[1])
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
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.", delete_after=5)
            return
        id = int(" ".join(args).strip())
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
                song = Song(
                    title=songdb.title,
                    url=songdb.url,
                    thumbnail_url=songdb.thumbnail_url,
                    webpage_url=songdb.webpage_url,
                )
            if song is not None:
                player.queue.append(song)
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

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}) -> bool:
        return configs["ENABLE_MUSIC"]


def setup(bot: ManChanBot):
    if Music.is_enabled(bot.configs):
        bot.add_cog(Music(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.Music")
