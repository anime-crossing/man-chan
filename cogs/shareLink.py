import logging
from typing import Any, Dict, cast

import spotipy
from discord.ext import commands
from discord.ext.commands.context import Context
from spotipy.oauth2 import SpotifyClientCredentials

from main import ManChanBot

from .commandbase import CommandBase


class ShareLink(CommandBase):
    def __init__(self, bot: ManChanBot):
        super().__init__(bot)
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=self.configs["SPOTIFY_CLIENT_ID"],
                client_secret=self.configs["SPOTIFY_CLIENT_SECRET"],
            )
        )

    @commands.command()
    async def track(self, ctx: Context, *args: str):
        join_words = " ".join(args).strip()
        results = self.sp.search(q=join_words, limit=1, type="track")
        await ctx.channel.send(
            results["tracks"]["items"][0]["external_urls"]["spotify"]
        )

    @commands.command()
    async def album(self, ctx: Context, *args: str):
        join_words = " ".join(args).strip()
        results = self.sp.search(q=join_words, limit=1, type="album")
        await ctx.channel.send(
            results["albums"]["items"][0]["external_urls"]["spotify"]
        )

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return (
            configs["ENABLE_SHARE_LINK"]
        )


async def setup(bot: ManChanBot):
    if ShareLink.is_enabled(bot.configs):
        await bot.add_cog(ShareLink(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.sharelink")
