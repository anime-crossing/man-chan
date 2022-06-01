from discord.ext import commands
from discord.ext.commands.context import Context

from db import Base, Child

from .base import CommandBase


class Test(CommandBase):
    @commands.command()
    async def create(self, ctx: Context, *args: str):
        join_words = " ".join(args)
        Base._create(temp=join_words)
        # Sends a message to the channel using the Context object.
        await ctx.channel.send("created")

    @commands.command()
    async def create2(self, ctx: Context, *args: str):
        join_words = " ".join(args)
        Child.create(col=join_words)
        # Sends a message to the channel using the Context object.
        await ctx.channel.send("created")

    @commands.command()
    async def list(self, ctx: Context):
        # Sends a message to the channel using the Context object.
        for i in Base.list():
            print(i.temp)

        res = ", ".join([b.temp for b in Base.list()])
        await ctx.channel.send(f"list: {res}")

    @commands.command()
    async def lists(self, ctx: Context):
        # Sends a message to the channel using the Context object.
        for i in Child.list():
            print(i.temp, i.col)

        res = ", ".join([f"({b.temp}, {b.col})" for b in Child.list()])
        await ctx.channel.send(f"list: {res}")
