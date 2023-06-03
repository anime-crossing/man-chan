from __future__ import annotations

import logging
from typing import TYPE_CHECKING
import disnake
from disnake.ext.commands import command

from utils.distyping import Context
from service.music import MasterPlayer
from .commandbase import CommandBase

if TYPE_CHECKING:
    from utils.distyping import ManChanBot

class Music(CommandBase):
    def __init__(self, bot: ManChanBot):
        self.bot = bot
        self.master_player = MasterPlayer()
        self.Embed = disnake.Embed(title="MANCHAN RADIO")

    @command()
    async def setup_music(self, ctx: Context):
        guild_id = ctx.guild.id
        if (not guild_id):
             return await ctx.channel.send("Please restart", delete_after= 5)
        if (self.master_player.getPlayer(guild_id) and 
            self.master_player.getPlayer(guild_id).channel_id and
            self.master_player.getPlayer(guild_id).player_ui):
            return await ctx.channel.send("channel is made", delete_after= 5)
        channel = await ctx.guild.create_text_channel(name="manchan radio")
        player_ui = await channel.send(embed=self.Embed)
        self.master_player.createPlayer(guild_id)
        self.master_player.getPlayer(guild_id).set_channel_id(channel.id)
        self.master_player.getPlayer(guild_id).set_player_ui(player_ui)
        await ctx.message.delete()

    @command()
    async def play(self, ctx: Context, *args: str):
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return

        if player.is_paused:
            player.is_paused = False
            player.is_playing = True
            player.voice_client.resume()
            return await ctx.send('Audio is now resumed', delete_after= 5)

        voice = ctx.author.voice
        if voice is None:
            return await ctx.send("Connect to a voice channel!", delete_after= 5)
        if  not player.is_connected:
            player.voice_client = await voice.channel.connect() # type: ignore
            await ctx.send("Connected", delete_after= 5)
            player.is_connected = True

        await ctx.message.delete()
        if player.is_playing == False:
            player.play_music()

    @command()
    async def queue(self, ctx: Context):
        songs = ''
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return
        for i in range(0, len(player.queue.queue)):
            songs += player.queue.queue[i]['title'] + '\n'
        if songs == '':
            return await ctx.channel.send("no songs", delete_after= 5)
        return await ctx.channel.send(songs, delete_after= 20)
    
    @command()
    async def leave(self, ctx: Context):
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.channel:
            return await ctx.send('Not connected to any voice channel.', delete_after= 5)
        player.leave_voice()
        await voice_client.disconnect()
        await ctx.send("Disconnected", delete_after= 5)
        await ctx.message.delete()

    @command()
    async def add(self, ctx: Context, *args: str):
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return
        player.queue.add_song(" ".join(args).strip())
        await ctx.message.delete()
        
    @command()
    async def history(self, ctx: Context):
        songs = ''
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return
        for i in range(0, len(player.queue.session_queue)):
            songs += player.queue.session_queue[i]['title'] + '\n'
        if songs == '':
            return await ctx.channel.send("no songs", delete_after= 5)
        await ctx.message.delete()
        return await ctx.channel.send(songs, delete_after= 20)
    
    @command()
    async def clear(self, ctx: Context):
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return
        
        if player.is_connected:
            player.clear_queue()
        await ctx.message.delete()

    @command()
    async def skip(self, ctx: Context):
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return
        
        if player.is_connected:
            player.stop_player()
        await ctx.message.delete()

    @command()
    async def pause(self, ctx: Context):
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return
        
        if player.is_playing:
            player.is_paused = True
            player.is_playing = False
            player.voice_client.pause()
            await ctx.send('Audio is now Paused', delete_after= 5)
        elif player.is_paused:
            player.is_paused = False
            player.is_playing = True
            player.voice_client.resume()
            await ctx.send('Audio is now resumed', delete_after= 5)
        await ctx.message.delete()

    @command()
    async def status(self, ctx: Context):
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return
        
        status = player.get_status()
        await ctx.message.delete()
        return await ctx.send(status)
    
    @command()
    async def np(self, ctx: Context):
        guild_id = ctx.guild.id
        player = self.master_player.getPlayer(guild_id)
        if not player.get_channel_id() == ctx.channel.id:
            return
        if not player.current_song == []:
            nowplaying = 'NOW PLAYING: ' + player.current_song['title']
            await ctx.send(nowplaying, delete_after= 5)
        await ctx.message.delete()
        return
        
def setup(bot: ManChanBot):
    if Music.is_enabled():
        bot.add_cog(Music(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.Music")
