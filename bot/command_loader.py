import logging
from os import listdir
from os.path import isdir
from os.path import join as osjoin
from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from utils.distyping import ManChanBot


class CommandLoader:
    _exclusion = {"__init__.py", "base.py"}

    def __init__(self, bot: "ManChanBot"):
        self._bot = bot

    def refresh_commands(self):
        logging.info("Loading commands...")
        for cog in self._get_available_cogs():
            self.add_command(cog)

        logging.info("Loading plugins commands...")
        for plugins in self._get_available_plugins():
            self.add_command(plugins)

    def add_command(self, command: str):
        logging.info(f"Loading module {command}")
        # This will run setup() on each Cog module it loads.
        self._bot.load_extension(command)

    def _get_available_cogs(self) -> Generator[str, None, None]:
        for file in listdir("cogs"):
            if self._is_valid_file(file):
                yield self._format_file_name(file, "cogs")

    def _get_available_plugins(self) -> Generator[str, None, None]:
        for folder in listdir("plugins"):
            if isdir(osjoin("plugins", folder)):
                for file in listdir(osjoin("plugins", folder)):
                    if self._is_valid_file(file):
                        yield self._format_file_name(file, f"plugins.{folder}")

    def _is_valid_file(self, file: str) -> bool:
        return file.endswith(".py") and file not in CommandLoader._exclusion

    def _format_file_name(self, file: str, dis_path: str) -> str:
        return f"{dis_path}.{file[:-3]}"
