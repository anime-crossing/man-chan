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


    def _get_spotify_info(self, results: Any, request_type: str):
        track_name = results[request_type]["items"][0]["name"]
        track_link = results[request_type]["items"][0]["external_urls"]["spotify"]
        track_artists = []
        for artist in results[request_type]["items"][0]["artists"]:
            track_artists.append(artist["name"])
        track_artists = ', '.join(track_artists)
        return track_name, track_artists, track_link

    @command()
    async def track(self, ctx: Context, *args: str):
        join_words = " ".join(args).strip()
        results = self.sp.search(q=join_words, limit=1, type="track")

        if not results:
            await ctx.channel.send("***No track found.***")
        else:
            track_name, track_artists, track_link = self._get_spotify_info(results, "tracks")
            await ctx.channel.send(f'[{track_name} - {track_artists}]({track_link})')

    @command()
    async def album(self, ctx: Context, *args: str):
        join_words = " ".join(args).strip()
        results = self.sp.search(q=join_words, limit=1, type="album")

        if not results:
            await ctx.channel.send("***No album found.***")
        else:
            album_name, album_artists, album_link = self._get_spotify_info(results, "albums")
            await ctx.channel.send(f'[{album_name} - {album_artists}]({album_link})')

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
