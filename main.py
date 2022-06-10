from typing import cast

import discord
from discord.ext.commands import Cog

from client import Client
from db.connection import setup_db_session


def load_commands(bot: Client):
    import inspect

    import cogs

    for _cls_name, cls in inspect.getmembers(cogs, inspect.isclass):
        if issubclass(cls, Cog) and cast(cogs.CommandBase, cls).is_enabled():
            bot.add_cog(cls(bot))


def main():
    from configs import configs

    intents = discord.Intents.default()
    intents.reactions = True
    intents.messages = True
    intents.guilds = True
    intents.members = True

    bot = Client(command_prefix="!", intents=intents)

    load_commands(bot)

    bot.run(configs.DISCORD_TOKEN)


if __name__ == "__main__":
    setup_db_session()
    main()
