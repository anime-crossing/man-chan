import logging
from typing import Any, Dict, cast

from discord.ext import commands
from discord.ext.commands.context import Context

from main import ManChanBot

from .commandbase import CommandBase

class Login(CommandBase):
    @commands.command()
    async def login(self, ctx: Context):
        # Create Embed with Python, reads from json config file
        await ctx.channel.send("Insert Embed Here")

async def setup(bot: ManChanBot):
    if Login.is_enabled():
        await bot.add_cog(Login(bot))
    else:
        logging.warn("SKIPPING: cogs.greetings")