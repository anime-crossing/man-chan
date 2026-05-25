import logging
from typing import Any, Dict, Optional

from disnake.ext import commands

from main import ManChanBot
from service.anilist.account_setup import AccountSetup
from service.anilist.ani_search import AniSearch
from service.anilist.leaderboard import Leaderboard
from utils.distyping import Context

from .commandbase import CommandBase


class Anilist(CommandBase):
    @commands.command(aliases=["ani"])
    async def anime(self, ctx: Context, *, arg: Optional[str] = None):
        if arg is None:
            await ctx.reply("Please provide search for command")
        else:
            await AniSearch(ctx).search_media(arg, "anime")

    @commands.command(aliases=["man"])
    async def manga(self, ctx: Context, *, arg: Optional[str] = None):
        if arg is None:
            await ctx.reply("Please provide search for command")
        else:
            await AniSearch(ctx).search_media(arg, "manga")

    @commands.command(aliases=["nov"])
    async def novel(self, ctx: Context, *, arg: Optional[str] = None):
        if arg is None:
            await ctx.reply("Please provide search for command")
        else:
            await AniSearch(ctx).search_media(arg, "novel")

    @commands.command(aliases=["aniacc"])
    async def aniaccount(self, ctx: Context):
        await AccountSetup(ctx).setup_account()

    @commands.command(aliases=["anilb", "alb"])
    async def anime_leaderboard(self, ctx: Context):
        await Leaderboard(ctx).leaderboard()

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs["ENABLE_ANILIST"]


def setup(bot: ManChanBot):
    if Anilist.is_enabled(bot.configs):
        bot.add_cog(Anilist(bot))
    else:
        logging.warn("SKIPPING: cogs.anilist")
