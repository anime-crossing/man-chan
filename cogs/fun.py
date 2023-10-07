from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from disnake.ext.commands import command

from utils.distyping import Context

from .commandbase import CommandBase

if TYPE_CHECKING:
    from utils.distyping import ManChanBot


class Fun(CommandBase):
    @command()
    async def ping(self, ctx: Context):
        await ctx.channel.send("Pong!")

    @command()
    async def choose(self, ctx: Context, *args: str):
        # Will randomly choose a selection of words delimited by commas
        options = "".join(args).split(",")
        await ctx.channel.send(random.choice(options).strip())


def setup(bot: ManChanBot):
    if Fun.is_enabled():
        bot.add_cog(Fun(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.fun")
