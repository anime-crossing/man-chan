from typing import Any, Dict

from disnake.ext.commands import Cog

from utils.distyping import ManChanBot


class CommandBase(Cog):
    def __init__(self, bot: ManChanBot):
        self.bot = bot

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return True

    @property
    def configs(self) -> Dict[str, Any]:
        return self.bot.configs


def setup(_):
    pass
