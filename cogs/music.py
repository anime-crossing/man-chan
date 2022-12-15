from discord.ext import commands
from discord.ext.commands.context import Context
from .commandbase import CommandBase
from typing import cast
from discord import VoiceClient
from utils.context import get_author_voice_channel
from main import ManChanBot
from utils.yt_dl import YTDHandler
import logging


class MusicPlayer(CommandBase):

    @commands.command()
    async def play(self, ctx: Context, *args: str):
        channel = get_author_voice_channel(ctx)

        if not channel:
            return
        self.bot.loop

        await channel.connect()
        if len(args) == 0:
            return

        file = await YTDHandler.from_url(ctx, args[0], self.bot.loop)

        print("CLASS:", ctx.voice_client.__class__)
        # voice_channel.play
        vc = cast(VoiceClient, ctx.voice_client)
        # channel.voice_state
        vc.play(file)


    @commands.command()
    async def leave(self, ctx: Context):
        voice_client = ctx.voice_client
        print(voice_client, voice_client.channel)
        if not voice_client or not voice_client.channel:
            return await ctx.send('Not connected to any voice channel.')
        
        await voice_client.disconnect(force=True)


async def setup(bot: ManChanBot):
    if MusicPlayer.is_enabled(bot.configs):
        await bot.add_cog(MusicPlayer(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.socialcredit")
