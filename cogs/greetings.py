from discord.ext import commands
from discord.ext.commands.context import Context

from .base import CommandBase
import random

class Greetings(CommandBase):
    @commands.command()
    async def ping(self, ctx: Context):
        print(type(ctx))
        # Sends a message to the channel using the Context object.
        await ctx.channel.send("pong")

    @commands.command()
    async def man(self, ctx: Context):
        # Sends a message to the channel using the Context object.
        await ctx.channel.send("chan")

    @commands.command()
    async def l(self, ctx: Context):
        # Sends a message to the channel using the Context object.
        await ctx.channel.send("L")

    @commands.command()
    async def choose(self, ctx: Context, *args):
        # Sends a message to the channel using the Context object.
        # need to fix separation of words counting as different arguments
        # should separate by commas
        join_words = " ".join(args)
        join_words = join_words.split(",")

        random_integer = random.randrange(len(join_words))
        await ctx.channel.send(join_words[random_integer])