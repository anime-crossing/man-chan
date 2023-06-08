from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from disnake.ext.commands import command

from utils.distyping import Context

from .commandbase import CommandBase

if TYPE_CHECKING:
    from utils.distyping import ManChanBot


class Music(CommandBase):
    def __init__(self, bot: ManChanBot):
        self.bot = bot
        self.master_player = bot.master_player
        # self.embed = Embed(title="MANCHAN RADIO")

    @command()
    async def setup_music(self, ctx: Context):
        guild_id = ctx.guild.id
        if (
            self.master_player.getPlayer(guild_id)
            and self.master_player.getPlayer(guild_id).channel_id
            and self.master_player.getPlayer(guild_id).player_ui
        ):
            return await ctx.channel.send("channel Already exists", delete_after=5)
        channel = await ctx.guild.create_text_channel(name="manchan radio")
        self.master_player.createPlayer(guild_id)
        player_ui = await channel.send(
            embed=self.master_player.getPlayer(guild_id).embed
        )
        self.master_player.getPlayer(guild_id).set_channel_id(channel.id)
        self.master_player.getPlayer(guild_id).set_player_ui(player_ui)
        await ctx.message.delete()

    @command()
    async def play(self, ctx: Context, *args: str):
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return ctx.send("Not in Music Channel", delete_after=5)

        await player.set_voice_client(ctx)
        if player.is_paused:
            player.is_paused = False
            player.is_playing = True
            player.voice_client.resume()
            return await ctx.send("Audio is now resumed", delete_after=5)

        await ctx.message.delete()
        if not player.is_playing:
            player.play_music()

    @command()
    async def queue(self, ctx: Context):
        guild_id = ctx.guild.id  # type: ignore
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:  # type: ignore
            return await ctx.send("Not in Music Channel", delete_after=5)
        if player.is_queue_empty():  # type: ignore
            return await ctx.channel.send("No songs in queue.", delete_after=5)
        songs = player.queue_to_string()  # type: ignore
        return await ctx.channel.send(songs, delete_after=20)

    @command()
    async def leave(self, ctx: Context):
        guild_id = ctx.guild.id  # type: ignore
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:  # type: ignore
            return ctx.send("Not in Music Channel", delete_after=5)
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.channel:
            return await ctx.send("Not connected to any voice channel.", delete_after=5)
        player.leave_voice()  # type: ignore
        await voice_client.disconnect()  # type: ignore
        await ctx.send("Disconnected", delete_after=5)
        await ctx.message.delete()

    @command()
    async def add(self, ctx: Context, *args: str):
        guild_id = ctx.guild.id  # type: ignore
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:  # type: ignore
            return ctx.send("Not in Music Channel", delete_after=5)
        player.add_song(" ".join(args).strip())  # type: ignore
        await ctx.message.delete()

    @command()
    async def history(self, ctx: Context):
        guild_id = ctx.guild.id  # type: ignore
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:  # type: ignore
            return ctx.send("Not in Music Channel", delete_after=5)
        if player.is_history_empty():  # type: ignore
            return await ctx.channel.send("no songs", delete_after=5)
        songs = player.history_to_string()  # type: ignore
        await ctx.message.delete()
        return await ctx.channel.send(songs, delete_after=20)

    @command()
    async def clear(self, ctx: Context):
        guild_id = ctx.guild.id  # type: ignore
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:  # type: ignore
            return ctx.send("Not in Music Channel", delete_after=5)

        if player.is_connected:  # type: ignore
            player.clear_queue()  # type: ignore
        await ctx.message.delete()

    @command()
    async def skip(self, ctx: Context):
        guild_id = ctx.guild.id  # type: ignore
        player = self.master_player.getPlayer(guild_id)  # type: ignore
        if not player.get_channel_id() == ctx.channel.id:  # type: ignore
            return ctx.send("Not in Music Channel", delete_after=5)

        if player.is_connected:  # type: ignore
            player.stop_player()  # type: ignore
        await ctx.message.delete()

    @command()
    async def pause(self, ctx: Context):
        guild_id = ctx.guild.id  # type: ignore
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:  # type: ignore
            return ctx.send("Not in Music Channel", delete_after=5)

        if player.is_playing:  # type: ignore
            player.is_paused = True  # type: ignore
            player.is_playing = False  # type: ignore
            player.voice_client.pause()  # type: ignore
            await ctx.send("Audio is now Paused", delete_after=5)
        elif player.is_paused:  # type: ignore
            player.is_paused = False  # type: ignore
            player.is_playing = True  # type: ignore
            player.voice_client.resume()  # type: ignore
            await ctx.send("Audio is now resumed", delete_after=5)
        await ctx.message.delete()

    @command()
    async def status(self, ctx: Context):
        guild_id = ctx.guild.id  # type: ignore
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:  # type: ignore
            return ctx.send("Not in Music Channel", delete_after=5)

        status = player.get_status()  # type: ignore
        await ctx.message.delete()
        return await ctx.send(status)

    @command(aliases=["np"])
    async def now_playing(self, ctx: Context):
        guild_id = ctx.guild.id  # type: ignore
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:  # type: ignore
            return ctx.send("Not in Music Channel", delete_after=5)
        if not player.current_song == None:  # type: ignore
            nowplaying = "NOW PLAYING: " + player.current_song.title  # type: ignore
            await ctx.send(nowplaying, delete_after=5)
        await ctx.message.delete()
        return


def setup(bot: ManChanBot):
    if Music.is_enabled():
        bot.add_cog(Music(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.Music")
