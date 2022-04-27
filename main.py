from discord import Client
from discord.ext import commands
import json

from client import Client
from cogs.greetings import Greetings


def main():
    bot = Client(command_prefix="!")

    bot.add_cog(Greetings(bot))
    configs = json.load(open("./configs.json"))
    bot.run(configs["token"])


if __name__ == "__main__":
    main()
