from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from disnake.ext.commands import command

from utils.config_mapper import CONCH_URL
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
        options = " ".join(args).split(",")
        await ctx.channel.send(random.choice(options).strip())

    @command(aliases=["8ball"])
    async def conch(self, ctx: Context, *args: str):
        pick = random.randint(0, 100)
        answer = None

        if pick < 5:  # 5% chance
            answer = "Maybe someday..."
        elif pick < 50:  # 45% chance
            answer = "Yes."
        elif pick < 90:  # 40% chance
            answer = "No."
        elif pick < 95:  # 5% chance
            answer = " # No."
        else:  # 5% chance
            answer = "I don't think so"

        image = self.configs.get(CONCH_URL, "")
        await ctx.channel.send(f"{answer} {image}".strip())


def setup(bot: ManChanBot):
    if Fun.is_enabled():
        bot.add_cog(Fun(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.fun")
