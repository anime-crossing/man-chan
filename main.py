import asyncio
import logging
from os import listdir
from typing import Generator

from disnake import Game, Intents
from disnake.ext.commands import Bot

from db.connection import DatabaseException, setup_db_session
from utils.yaml_loader import load_yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s | %(module)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class ManChanBot(Bot):
    def __init__(self):
        self.configs = {}
        self.db_on = False

    def run(self):
        logging.info(f"Starting bot...")
        asyncio.run(self._prepare_bot())

    async def on_ready(self):
        logging.info(f"{self.user.name} has connected to Discord!")
        if self.configs.get("PRESENCE_TEXT"):
            await self.change_presence(
                activity=Game(name=self.configs["PRESENCE_TEXT"])
            )

    async def _prepare_bot(self):
        logging.info("Loading configs.yaml...")
        self._load_config_settings()

        logging.info("Initializing client...")
        self._initialize_client()

        logging.info("Preparing database connection...")
        self._setup_db()

        logging.info("Loading commands...")
        await self._load_commands()

        logging.info("Booting up ManChan-gelions...")

        await self._start_client()

    def _load_config_settings(self):
        configs = load_yaml()

        # Check if essential Discord settings exist
        if len(configs) <= 0:
            raise ValueError(
                "Nothing in the configs.yaml was loaded!; Cannot start bot."
            )

        if "DISCORD_TOKEN" not in configs:
            raise ValueError("No DISCORD_TOKEN was given; Cannot start bot.")

        if "COMMAND_PREFIX" not in configs:
            raise ValueError("No COMMAND_PREFIX was given; Cannot start bot.")

        self.configs = configs
        self.configs["db_on"] = self.db_on

    def _initialize_client(self):
        super().__init__(
            command_prefix=self.configs["COMMAND_PREFIX"],
            intents=self._generate_intents(),
        )

    def _setup_db(self):
        if "DATABASE_URL" not in self.configs:
            if self.configs.get("FORCE_DATABASE", True):
                raise DatabaseException("No database was provided")
            logging.warning(
                "No database was provided, but will continue to run anyways."
            )
            self.db_on = False
            self.configs["db_on"] = self.db_on
            return

        setup_db_session(self.configs["DATABASE_URL"])
        self.db_on = True
        self.configs["db_on"] = self.db_on

    async def _load_commands(self):
        for module in self._iterate_modules():
            logging.info(f"Loading module {module}")
            # This will run setup() on each Cog module it loads.
            self.load_extension(module)  # type: ignore

    def _iterate_modules(self) -> Generator:
        for file in listdir("cogs"):
            if file.endswith(".py") and file not in {"__init__.py", "base.py"}:
                file_name = file[:-3]
                yield f"cogs.{file_name}"

    def _generate_intents(self):
        intents = Intents.all()
        intents.reactions = True
        intents.messages = True
        intents.guilds = True
        intents.message_content = True  # type: ignore - discord library typing
        intents.members = True
        return intents

    async def _start_client(self):
        await self.start(self.configs["DISCORD_TOKEN"])


if __name__ == "__main__":
    bot = ManChanBot()
    bot.run()
