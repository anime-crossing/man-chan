from discord.ext import commands
from discord.ext.commands.context import Context
from .commandbase import CommandBase
from typing import Any, Dict, cast
from discord import User, Member, VoiceState, VoiceChannel
from utils.context import get_member, get_author_voice_channel
import youtube_dl


class MusicPlayer(CommandBase):

    @commands.command()
    async def play(self, ctx: Context):
        channel = get_author_voice_channel(ctx)

        if not channel:
            return
        self.bot.loop

        await channel.connect()


    @commands.command()
    async def leave(self, ctx: Context):
        pass
