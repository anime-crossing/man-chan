import asyncio
import logging

from disnake import Game, Intents
from disnake.ext.commands import Bot

from bot.command_loader import CommandLoader
from db.connection import DatabaseException, setup_db_session, setup_plugins_db
from service.music import MasterPlayer
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
        self.db_plugins_on = False
        self.master_player = MasterPlayer()

    def run(self):
        logging.info(f"Starting bot...")
        asyncio.run(self._prepare_bot())

    async def on_ready(self):
        """
        Disnake function called when startup is finished
        """
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

        # Loading the cog and plugin commands
        CommandLoader(self).refresh_commands()

        logging.info("Booting up ManChan-gelions...")

        await self._start_client()

    def _load_config_settings(self):
        configs = load_yaml()

        # Check if essential Discord settings exist
        if len(configs) <= 0:
            raise ValueError(
                "Nothing in the configs.yaml was loaded! Cannot start bot."
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
            # Will always start bot without a database unless given an
            # env variable to not start without it.
            # Properly check database conditions on Cogs that require it.
            if self.configs.get("FORCE_DATABASE", True):
                raise DatabaseException("No database was provided")
            logging.warning(
                "No database was provided, but will continue to run anyways."
            )
            self.db_on = False
            self.configs["db_on"] = self.db_on
            return
        else:
            setup_db_session(self.configs["DATABASE_URL"])
            self.db_on = True
            self.configs["db_on"] = self.db_on

        if "PLUGINS_DB_URL" in self.configs:
            setup_plugins_db(self.configs["PLUGINS_DB_URL"])
            self.db_plugins_on = True
            self.configs["plugins_db_on"] = self.db_plugins_on

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
