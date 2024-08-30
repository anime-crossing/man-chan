from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict
from disnake.ext.commands import command

from db.player import Players
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
        player = self.master_player.getPlayer(ctx.guild.id)     #type: ignore[reportOptionalMemberAccess]
        if player is None: return self.player_does_exist_error(ctx)
        if not await self.in_music_channel(player, ctx): return

        await player.set_voice_client(ctx)

        if args != ():
            player.add_song(" ".join(args).strip())

        if player.is_paused:
            player.is_paused = False
            player.is_audio_buffered = True
            player.voice_client.resume()    # type: ignore
            return await ctx.send("Audio is now resumed", delete_after=5)

        await ctx.message.delete()
        if not player.is_audio_buffered:
            player.play_music()

    @command()
    async def queue(self, ctx: Context):
        player = self.master_player.getPlayer(ctx.guild.id)     #type: ignore[reportOptionalMemberAccess]
        if player is None: return self.player_does_exist_error(ctx)
        if not await self.in_music_channel(player, ctx): return
        if player.is_queue_empty():
            return await ctx.channel.send("No songs in queue.", delete_after=5)
        await ctx.message.delete()
        return await ctx.channel.send(player.queue_to_string(), delete_after=20)

    @command()
    async def leave(self, ctx: Context):
        player = self.master_player.getPlayer(ctx.guild.id)     #type: ignore[reportOptionalMemberAccess]
        if player is None: return self.player_does_exist_error(ctx)
        if not await self.in_music_channel(player, ctx): return
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.channel:
            return await ctx.send("Not connected to any voice channel.", delete_after=5)
        player.leave_voice()
        await voice_client.disconnect(force= False)  
        await ctx.send("Disconnected", delete_after=5)
        await ctx.message.delete()

    @command()
    async def add(self, ctx: Context, *args: str):
        player = self.master_player.getPlayer(ctx.guild.id)     #type: ignore[reportOptionalMemberAccess]
        if player is None: return self.player_does_exist_error(ctx)
        if not await self.in_music_channel(player, ctx): return
        player.add_song(" ".join(args).strip())
        await ctx.message.delete()

    @command()
    async def history(self, ctx: Context):
        player = self.master_player.getPlayer(ctx.guild.id)     #type: ignore[reportOptionalMemberAccess]
        if player is None: return self.player_does_exist_error(ctx)
        if not await self.in_music_channel(player, ctx): return
        if player.is_history_empty():
            return await ctx.channel.send("no songs", delete_after=5)
        await ctx.message.delete()
        return await ctx.channel.send(player.history_to_string(), delete_after=20)

    @command()
    async def clear(self, ctx: Context):
        player = self.master_player.getPlayer(ctx.guild.id)     #type: ignore[reportOptionalMemberAccess]
        if player is None: return self.player_does_exist_error(ctx)
        if not await self.in_music_channel(player, ctx): return
        if player.is_connected: 
            player.clear_queue()  
        await ctx.message.delete()

    @command()
    async def skip(self, ctx: Context):
        player = self.master_player.getPlayer(ctx.guild.id)     #type: ignore[reportOptionalMemberAccess]
        if player is None: return self.player_does_exist_error(ctx)
        if not await self.in_music_channel(player, ctx): return
        if player.is_connected: 
            player.stop_player()  
        await ctx.message.delete()

    @command()
    async def pause(self, ctx: Context):
        player = self.master_player.getPlayer(ctx.guild.id)     #type: ignore[reportOptionalMemberAccess]
        if player is None: return self.player_does_exist_error(ctx)
        if not await self.in_music_channel(player, ctx): return

        if player.is_audio_buffered:  
            player.is_paused = True  
            player.is_audio_buffered = False  
            player.voice_client.pause()  # type: ignore
            await ctx.send("Audio is now Paused", delete_after=5)
        elif player.is_paused:  
            player.is_paused = False  
            player.is_audio_buffered = True  
            player.voice_client.resume()  # type: ignore
            await ctx.send("Audio is now resumed", delete_after=5)
        await ctx.message.delete()

    @command()
    async def status(self, ctx: Context):
        player = self.master_player.getPlayer(ctx.guild.id)     #type: ignore[reportOptionalMemberAccess]
        if player is None: return self.player_does_exist_error(ctx)
        if not await self.in_music_channel(player, ctx): return
        status = player.get_status()  
        await ctx.message.delete()
        return await ctx.send(status)

    @command(aliases=["np"])
    async def now_playing(self, ctx: Context):
        player = self.master_player.getPlayer(ctx.guild.id)     #type: ignore[reportOptionalMemberAccess]
        if player is None: return self.player_does_exist_error(ctx)
        if not await self.in_music_channel(player, ctx): return
        if not player.current_song == None: 
            nowplaying = "NOW PLAYING: " + player.current_song.title 
            await ctx.send(nowplaying, delete_after=5)
        await ctx.message.delete()
        return
    
    async def in_music_channel(self, player: Player, ctx: Context) -> bool:
        if not player.get_channel_id() == ctx.channel.id:
            await ctx.send("Not in Music Channel", delete_after=5)
            return False
        return True
    
    async def player_does_exist_error(self, ctx: Context) -> None:
        await ctx.channel.send("Player does not Exist. Please use !setup_music", delete_after=10)

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}) -> bool:
        return configs["ENABLE_MUSIC"]

def setup(bot: ManChanBot):
    if Music.is_enabled(bot.configs):
        bot.add_cog(Music(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.Music")
