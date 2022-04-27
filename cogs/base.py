from discord.ext import commands
from discord.ext.commands import Cog

from client import Client


class CommandBase(Cog):
    def __init__(self, bot: Client):
        self.bot = bot
