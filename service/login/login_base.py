from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from disnake import Color, Embed

from utils.config_mapper import LOGIN_FILE_PATH

from ..base import ServiceBase

if TYPE_CHECKING:
    from utils.distyping import Config, Context


class LoginBase(ServiceBase):
    def __init__(self, ctx: Context, configs: Config):
        super().__init__(ctx, configs)

    @property
    def logins(self) -> Dict[str, Dict[str, Any]]:
        return self._logins

    @logins.setter
    def logins(self, login_data: Dict[str, Dict[str, Any]]):
        self._logins = login_data

    @classmethod
    def open_json(cls, path: Optional[str]) -> bool:
        # Checks to see if File Exists
        if path is None:
            cls._logins = dict()
            return False

        file = Path(path)
        if file.exists() and file.is_file():
            try:
                # Check to see if JSON File opens properly
                with file.open(encoding="utf-8") as f:
                    cls._logins = json.loads(f.read())
                    return True
            except json.decoder.JSONDecodeError:
                logging.warn("JSON File is not valid")
            except IOError:
                logging.warn(f"Error opening {LOGIN_FILE_PATH}")

        cls._logins = dict()
        return False

    def create_broken_file_error_embed(self) -> Embed:
        embed = Embed()
        embed.title = "JSON File Broken"
        embed.description = "Please contact Bot Admins to Fix"
        embed.color = Color.red()

        return embed

    def is_login_empty(self) -> bool:
        return len(self.logins) < 1
