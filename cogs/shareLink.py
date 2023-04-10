from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict

import spotipy
from disnake.ext.commands import command
from spotipy.oauth2 import SpotifyClientCredentials

from utils.config_mapper import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_ENABLE_SHARE,
)
from utils.distyping import Context

from .commandbase import CommandBase

if TYPE_CHECKING:
    from utils.distyping import ManChanBot


class ShareLink(CommandBase):
    def __init__(self, bot: ManChanBot):
        super().__init__(bot)
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=self.configs[SPOTIFY_CLIENT_ID],
                client_secret=self.configs[SPOTIFY_CLIENT_SECRET],
            )
        )

    @command()
    async def track(self, ctx: Context, *args: str):
        join_words = " ".join(args).strip()
        results = self.sp.search(q=join_words, limit=1, type="track")

        if not results:
            await ctx.channel.send("***No track found.***")
        else:
            await ctx.channel.send(
                results["tracks"]["items"][0]["external_urls"]["spotify"]
            )

    @command()
    async def album(self, ctx: Context, *args: str):
        join_words = " ".join(args).strip()
        results = self.sp.search(q=join_words, limit=1, type="album")

        if not results:
            await ctx.channel.send("***No track found.***")
        else:
            await ctx.channel.send(
                results["albums"]["items"][0]["external_urls"]["spotify"]
            )

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return (
            configs.get(SPOTIFY_ENABLE_SHARE)
            and configs.get(SPOTIFY_CLIENT_ID)
            and configs.get(SPOTIFY_CLIENT_SECRET)
        )


def setup(bot: ManChanBot):
    if ShareLink.is_enabled(bot.configs):
        bot.add_cog(ShareLink(bot))
    else:
        logging.warn("SKIPPING: cogs.sharelink")
