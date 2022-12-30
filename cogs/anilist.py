import datetime
import logging
import operator
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
            if date["day"] is None:
                return date["year"] if date["year"] != None else "?"
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

        json_response = requests.post(
            anilist_url, json={"query": query, "variables": variables}
        ).json()
        return json_response["data"]["Media"]

    async def search_embed(self, ctx: Context, type: str, media: str, format: Any):
        anilist_url = self.configs["ANILIST_URL"]
        query = '''
        query($type: MediaType, $format: MediaFormat $page: Int, $perPage: Int, $search: String){
            Page(page: $page, perPage: $perPage){
                pageInfo{
                    total
                    currentPage
                    lastPage
                    hasNextPage
                    perPage
                }
                media(search: $search, type: $type, format: $format){
                    id
                    title{
                        romaji
                    }
                    studios(isMain: true){
                        nodes{
                            name
                        }
                    }
                    popularity
                }
            }
        }
        '''
        variables = {"type": type, "search": media}
        if format is not None:
            variables = {"type": type, "search": media, "format": format}
        json_response = requests.post(anilist_url, json={"query": query, "variables": variables}).json()

        search_number = json_response['data']['Page']['pageInfo']['total']
        search_query = json_response['data']['Page']['media']
        search_query.sort(key=operator.itemgetter('popularity'), reverse=True)
        
        selection_embed = Embed()
        selection_embed.title = "Search Results"
        selection_embed.description = "Please select the entry using the menu below."
        
        field_value = ""
        
        select = Select(
            placeholder="Select an entry"
        )

        for i, item in enumerate(search_query):
            field_value += f"`{i+1}`.`♡{item['popularity']}` · {item['studios']['nodes'][0]['name']} · {'*' * 2}{item['title']['romaji']}{'*' * 2}\n"
            select.add_option(
                label=f"{i+1}. {item['title']['romaji']}",
                description=item['studios']['nodes'][0]['name'])

        selection_embed.add_field(
            name=f"Showing entries of 1-{search_number} of {search_number}",
            value=field_value,
            inline = True
        )

        view = View()
        view.add_item(select)

        await ctx.reply(content=f"Total results: {search_number}",embed=selection_embed, view=view, mention_author=False) #type: ignore

    async def create_message(self, ctx: Context, type: str, media_json: Dict[str, Any]):
        embed = Embed()
        embed.color = Color.blue()

        image_url = media_json["coverImage"]["extraLarge"]
        embed.title = media_json["title"]["romaji"]
        embed.url = media_json["siteUrl"]
        embed.description = media_json["description"]
        embed.set_thumbnail(url=image_url)

        information_string = f"Type: {media_json['type'] if media_json['format'] != 'NOVEL' else 'NOVEL'}\nStatus: {media_json['status']}\n"

        if type == "ANIME":
            information_string += f"AIRED: {Anilist.convert_date(media_json['startDate'])} to {Anilist.convert_date(media_json['endDate'])}\n"
            information_string += f"Episodes: {media_json['episodes'] if media_json['episodes'] != None else '?'}\n"
        else:
            information_string += f"From: {Anilist.convert_date(media_json['startDate'])} to {Anilist.convert_date(media_json['endDate'])}\n"
            information_string += f"Chapters: {media_json['chapters'] if media_json['chapters'] != None else '?'}\n"
            information_string += f"Volumes: {media_json['volumes'] if media_json['volumes'] != None else '?'}\n"

        information_string += f"Score: {media_json['averageScore']}"

        embed.add_field(name="Information", value=information_string, inline=True)

        embed.add_field(
            name="Genre", value=("\n".join(media_json["genres"])), inline=True
        )

        embed.set_footer(text="Stats and information provided by Anilist")

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

        await ctx.reply(embed=embed, view=view, mention_author=False)  # type: ignore - View is Valid

    @commands.command(aliases=["ani"])
    async def anime(self, ctx: Context, *, arg: str = None):  # type: ignore - yes i can
        if arg is None:
            await ctx.reply("Please provide search for command")
        else:
            await self.create_message(
                ctx, "ANIME", self.media_search("ANIME", str(arg), None)
            )

    @commands.command(aliases=["man"])
    async def manga(self, ctx: Context, *, arg: str = None):  # type: ignore - yes i can
        if arg is None:
            await ctx.reply("Please provide search for command")
        else:
            await self.create_message(
                ctx, "MANGA", self.media_search("MANGA", str(arg), "MANGA")
            )

    @commands.command(aliases=["nov"])
    async def novel(self, ctx: Context, *, arg: str = None):  # type: ignore - yes i can
        if arg is None:
            await ctx.reply("Please provide search for command")
        else:
            await self.create_message(
                ctx, "MANGA", self.media_search("MANGA", str(arg), "NOVEL")
            )
    @commands.command()
    async def search(self, ctx: Context):    #type:ignore - yes i can
        await self.search_embed(ctx, "ANIME", "Sound Euphonium", None)

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs["ENABLE_ANILIST"] and configs["ANILIST_URL"]


async def setup(bot: ManChanBot):
    if Anilist.is_enabled(bot.configs):
        await bot.add_cog(Anilist(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.anilist")
