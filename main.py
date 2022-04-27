import json

from discord.ext.commands import Cog

from client import Client


def load_commands(bot: Client):
    import inspect

    import cogs

    for _cls_name, cls in inspect.getmembers(cogs, inspect.isclass):
        if issubclass(cls, Cog):
            bot.add_cog(cls(bot))


def main(configs: dict):
    bot = Client(command_prefix="!")

    load_commands(bot)

    bot.run(configs["token"])


if __name__ == "__main__":
    configs = json.load(open("./configs.json"))
    main(configs)
