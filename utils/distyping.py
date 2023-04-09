from typing import Any, Dict

from disnake.ext import commands

from main import ManChanBot

# For typing
Context = commands.Context[ManChanBot]
Config = Dict[str, Any]
