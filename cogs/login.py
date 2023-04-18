from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict

from disnake.ext.commands import command

from service.login import LoginInfo
from utils.config_mapper import LOGIN_ENABLE, LOGIN_FILE_PATH, LOGIN_INFO_TIMEOUT
from utils.distyping import Config, Context

from .commandbase import CommandBase

if TYPE_CHECKING:
    from utils.distyping import ManChanBot


class Login(CommandBase):
    @command()
    async def login(self, ctx: Context):
        """Returns an interactive embed based on a provided json filled with login info."""
        service = LoginInfo(ctx, self.centralized_configs)

        if service.is_login_empty():
            embed = service.create_broken_file_error_embed()
            await ctx.send(embed=embed)
            return

        await service.send_login_interaction()

    @property
    def login_info_timeout(self) -> int:
        return self.configs.get(LOGIN_INFO_TIMEOUT, 15)

    @property
    def centralized_configs(self) -> Config:
        return {
            LOGIN_ENABLE: self.configs[LOGIN_ENABLE],
            LOGIN_FILE_PATH: self.configs[LOGIN_FILE_PATH],
            LOGIN_INFO_TIMEOUT: self.login_info_timeout,
        }

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}) -> bool:
        path = configs.get(LOGIN_FILE_PATH)
        return bool(configs.get(LOGIN_ENABLE) and LoginInfo.open_json(path))


def setup(bot: ManChanBot):
    if Login.is_enabled(bot.configs):
        bot.add_cog(Login(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.login")
