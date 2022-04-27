import discord
from discord.ext import commands

class Greetings(discord.ext.commands.Cog, name='Greetings module'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
	# Sends a message to the channel using the Context object.
        await ctx.channel.send("pong")

    @commands.command()
    async def man(self, ctx):
	# Sends a message to the channel using the Context object.
        await ctx.channel.send("chan")

    @commands.command()
    async def l(self, ctx):
	# Sends a message to the channel using the Context object.
        await ctx.channel.send("L")


