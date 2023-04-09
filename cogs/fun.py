import logging
import random

from disnake.ext import commands

from utils.distyping import Context, ManChanBot

from .commandbase import CommandBase


class Fun(CommandBase):
    @commands.command()
    async def ping(self, ctx: Context):
        print(type(ctx))
        # Sends a message to the channel using the Context object.
        await ctx.channel.send("pong")

    @commands.command()
    async def choose(self, ctx: Context, *args: str):
        # Sends a message to the channel using the Context object.
        join_words = " ".join(args).split(",")
        await ctx.channel.send(random.choice(join_words))


def setup(bot: ManChanBot):
    if Fun.is_enabled():
        bot.add_cog(Fun(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.fun")
