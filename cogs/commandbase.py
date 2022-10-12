from typing import Any, Dict

from discord.ext.commands import Cog

from main import ManChanBot


class CommandBase(Cog):
    def __init__(self, bot: ManChanBot):
        self.bot = bot

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return True

    @property
    def configs(self) -> Dict[str, Any]:
        return self.bot.configs


async def setup(_):
    pass
