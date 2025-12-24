from typing import Any, Dict
from cogs.commandbase import CommandBase
from main import ManChanBot
from disnake.ext.commands import command
from service.jellyfin import JellySeerApi
from service.jellyfin.ui import Dropdown, ResultsEmbed
from utils.config_mapper import ENABLE_JELLYSEERR, JELLYSEERR_API_KEY, JELLYSEERR_BASE_URL, ROOT_FOLDER_MOVIE, ROOT_FOLDER_TV
from utils.distyping import Context
from disnake.ui import View
import logging

class Jellyseer(CommandBase):
    def __init__(self, bot: ManChanBot):
        self.bot = bot
        self.jellyseerApi = JellySeerApi(self.configs[JELLYSEERR_API_KEY], self.configs[JELLYSEERR_BASE_URL], self.configs[ROOT_FOLDER_MOVIE], self.configs[ROOT_FOLDER_TV])

    @command(aliases=["req"])
    async def request(self, ctx: Context, *args: str):
        query = " ".join(args).strip()
        results = self.jellyseerApi.search(query)
        if len(results) == 0:
            await ctx.channel.send(f"No results for - {query}")
            return
        embed = ResultsEmbed(results)
        view = View()
        view.add_item(Dropdown(self.jellyseerApi, results))
        await ctx.channel.send(embed=embed, view=view)

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return (
            configs.get(ENABLE_JELLYSEERR)
            and configs.get(JELLYSEERR_API_KEY)
            and configs.get(JELLYSEERR_BASE_URL)
        )

def setup(bot: ManChanBot):
    if Jellyseer.is_enabled(bot.configs):
        bot.add_cog(Jellyseer(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.Jellyseer")