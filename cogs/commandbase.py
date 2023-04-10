from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from disnake.ext.commands import Cog

if TYPE_CHECKING:
    from utils.distyping import Config, ManChanBot


class CommandBase(Cog):
    def __init__(self, bot: ManChanBot):
        self.bot = bot

    @classmethod
    def is_enabled(cls, configs: Config = {}):
        return True

    @property
    def configs(self) -> Dict[str, Any]:
        return self.bot.configs


def setup(_):
    pass
