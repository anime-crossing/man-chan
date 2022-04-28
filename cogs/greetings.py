import random

from discord.ext import commands
from discord.ext.commands.context import Context

from .base import CommandBase


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
    async def choose(self, ctx: Context, *args: str):
        # Sends a message to the channel using the Context object.
        join_words = " ".join(args).split(",")
        await ctx.channel.send(random.choice(join_words))
