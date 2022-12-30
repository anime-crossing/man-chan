import datetime
import logging
from typing import Any, Dict

import requests
from discord import Interaction  # type: ignore - Interaction exists
from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, Select, View  # type: ignore - These libraries exist

from main import ManChanBot

from .commandbase import CommandBase


class Anilist(CommandBase):
    @staticmethod
    def convert_date(date: Dict[str, Any]) -> str:
        if date["month"] is None:
            return "?"
        month_num = str(date["month"])
        datetime_object = datetime.datetime.strptime(month_num, "%m")
        month_name = datetime_object.strftime("%b")

        return f"{month_name} {date['day']}, {date['year']}"

    def media_search(self, type: str, media: str, format: Any):
        anilist_url = self.configs["ANILIST_URL"]

        query = """
        query ($type: MediaType, $search: String, $format: MediaFormat){
            Media(search: $search, type: $type, format: $format){
                id
                title{
                    romaji
                }
                type
                format
                status
                description
                episodes
                coverImage {
                    extraLarge
                }
                siteUrl
                averageScore
                genres
                startDate {
                    year
                    month
                    day
                }
                endDate {
                    year
                    month
                    day
                }
                chapters
                volumes
            }
        }
        """

        variables = {"type": type, "search": media}
        if format is not None:
            variables = {"type": type, "search": media, "format": format}

        return requests.post(anilist_url, json={"query": query, "variables": variables})

    @commands.command(aliases=["ani"])
    async def anime(self, ctx: Context, *, arg: str):

        json_response = self.media_search("ANIME", str(arg), None)

        data = json_response.json()
        data = data["data"]["Media"]

        embed = Embed()
        embed.color = Color.blue()

        # Do Stuff to get Query Here
        image_url = data["coverImage"]["extraLarge"]
        embed.title = data["title"]["romaji"]
        embed.url = data["coverImage"]["extraLarge"]
        embed.description = data["description"]
        embed.set_thumbnail(url=image_url)
        embed.add_field(
            name="Information",
            value=(
                f"Type: {data['type']}\nStatus: {data['status']}\nAIRED: {Anilist.convert_date(data['startDate'])} to {Anilist.convert_date(data['endDate'])}\nEpisodes: {data['episodes'] if data['episodes'] != None else '?'}\nScore: {data['averageScore']}"
            ),
            inline=True,
        )
        embed.add_field(name="Genre", value="Comedy\nMusic\nSlice of Life", inline=True)
        embed.set_footer(text="hi")

        async def magnifying_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            if interaction.user == ctx.author:
                embed.set_thumbnail(url=None)  # type: ignore - None is valid
                embed.set_image(url=image_url)

                stats_button = Button(emoji="📊")
                stats_button.callback = stat_callback
                stat_view = View()
                stat_view.add_item(stats_button)

                await interaction.response.edit_message(embed=embed, view=stat_view)

        async def stat_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            if interaction.user == ctx.author:
                embed.set_image(url=None)  # type: ignore - None is valid
                embed.set_thumbnail(url=image_url)

                await interaction.response.edit_message(embed=embed, view=view)

        magnifying_button = Button(emoji="🔍")
        magnifying_button.callback = magnifying_callback

        view = View()
        view.add_item(magnifying_button)

        await ctx.reply(embed=embed, view=view, mention_author=False)  # type: ignore - View exists

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs["ENABLE_ANILIST"] and configs["ANILIST_URL"]


async def setup(bot: ManChanBot):
    if Anilist.is_enabled(bot.configs):
        await bot.add_cog(Anilist(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.anilist")
