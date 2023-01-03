import datetime
import logging
import operator
from typing import Any, Dict, Optional

import requests
from discord import Interaction  # type: ignore - Interaction exists
from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, Select, View, Modal, TextInput  # type: ignore - These libraries exist

from db.anilist_users import AnilistUsers
from main import ManChanBot
# from utils.context import get_member

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

    def media_fetch(self, media_id: int):
        anilist_url = self.configs["ANILIST_URL"]

        query = """
        query ($id: Int){
            Media(id: $id){
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

        variables = {"id": media_id}

        json_response = requests.post(
            anilist_url, json={"query": query, "variables": variables}
        ).json()

        return json_response["data"]["Media"]

    def fetch_score(self, media_id: int, user_id: Optional[int]):
        anilist_url = self.configs["ANILIST_URL"]

        if not user_id:
            return
            
        query = """
        query ($user: Int, $id: Int){
            MediaList(userId: $user, mediaId: $id){
                user{
                    name
                }
                score(format: POINT_10_DECIMAL)
                status
                progress
            }
        }
        """

        variables = {"user": user_id, "id": media_id}

        json_response = requests.post(
            anilist_url, json={"query": query, "variables": variables}
        ).json()

        if "errors" not in json_response:
            return json_response["data"]["MediaList"]

    async def create_setup_embed(self, ctx: Context):
        account_embed = Embed(
            title="Anilist Account Setup", 
            description="Please use the button below to enter your Anilist Username",
            color=Color.blue()
        )

        modal = Modal(title="Enter Anilist Username")
        text_input = TextInput(label='username')
        
        async def modal_callback(interaction: Interaction):
            await self.profile_query(ctx, interaction, text_input)

        modal.add_item(text_input)
        modal.on_submit = modal_callback

        async def test_callback(interaction: Interaction):
           await interaction.response.send_modal(modal)

        button = Button(emoji='✏️')
        button.callback = test_callback

        view = View()
        view.add_item(button)

        await ctx.send(embed=account_embed, view=view)

    async def profile_query(self, ctx: Context, interaction: Interaction, anilist_id: str):
        anilist_url = self.configs["ANILIST_URL"]
        query = '''
        query ($name: String){
            User(name: $name){
                id
                name
                avatar{
                    large
                }
                siteUrl
            }
        }
        '''

        variables = {"name" : str(anilist_id)}

        json_response = requests.post(url=anilist_url, json={"query" : query, "variables" : variables}).json()
        account_info = json_response['data']['User']

        profile_embed = Embed(
            title="User Found",
            description=f"Is this your account: {account_info['name']}",
            color=Color.blue(),
            url=account_info['siteUrl']
        )
        profile_embed.set_thumbnail(url=account_info['avatar']['large'])

        yes_button = Button(emoji="✅")

        async def yes_callback(interaction: Interaction):
            profile_embed.color = Color.green()
            profile_embed.description = "Account Info Saved to Bot."

            await interaction.response.edit_message(embed=profile_embed, view=None)
            await self.save_anilist_id(ctx, account_info['id'])
            

        yes_button.callback = yes_callback

        view = View()
        view.add_item(yes_button)

        await interaction.response.edit_message(embed=profile_embed, view=view)
    
    async def save_anilist_id(self, ctx: Context, anilist_id: int):
        discord_id = ctx.author.id
        table_entry = AnilistUsers.get(discord_id)

        if not table_entry:
            table_entry = AnilistUsers.create(discord_id)
        
        table_entry.set_anilist_id(anilist_id)

    async def search_embed(self, ctx: Context, type: str, media: str, format: Any):
        anilist_url = self.configs["ANILIST_URL"]
        query = """
        query ($type: MediaType, $format: MediaFormat, $page: Int, $perPage: Int, $search: String) {
            Page(page: $page, perPage: $perPage) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                    perPage
                }
                media(search: $search, type: $type, format: $format) {
                    id
                    title {
                        romaji
                    }
                    studios(isMain: true) {
                        nodes {
                            name
                        }
                    }
                    staff(perPage: 2){
                        edges{
                            role
                        }
                        nodes{
                            name {
                                full
                            }
                        }
                    }
                    popularity
                }
            }
        }
        """
        variables = {"type": type, "search": media, "page": 1, "perPage": 10}
        if format is not None:
            variables = {
                "type": type,
                "search": media,
                "page": 1,
                "perPage": 10,
                "format": format,
            }
        json_response = requests.post(
            anilist_url, json={"query": query, "variables": variables}
        ).json()

        search_number = json_response["data"]["Page"]["pageInfo"]["perPage"]
        search_query = json_response["data"]["Page"]["media"]
        search_query.sort(key=operator.itemgetter("popularity"), reverse=True)

        selection_embed = Embed()
        selection_embed.title = "Search Results"
        selection_embed.description = "Please select the entry using the menu below."

        field_value = ""

        select = Select(placeholder="Select an entry")

        for i, item in enumerate(search_query):
            if type == "ANIME":
                staff_name = item.get("studios", {}).get("nodes", [])
                if staff_name:
                    staff_name = staff_name[0].get("name", "Unknown Studio")
                else:
                    staff_name = "Unknown Studio"
            else:
                if item["staff"]["nodes"]:
                    staff_name = item["staff"]["nodes"][0]["name"]["full"]
                    if item["staff"]["edges"][0]["role"] != "Story & Art":
                        staff_name += f", {item['staff']['nodes'][1]['name']['full']}"
                else:
                    staff_name = "Unknown Author"

            field_value += f"`{i+1}`.`♡{item['popularity']}` · {staff_name} · {'*' * 2}{item['title']['romaji']}{'*' * 2}\n"
            select.add_option(
                label=f"{i+1}. {item['title']['romaji']}",
                value=item["id"],
                description=staff_name,
            )

        selection_embed.add_field(
            name=f"Showing entries of 1-{search_number} of {search_number}",
            value=field_value,
            inline=True,
        )

        async def selection_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            if interaction.user == ctx.author:
                await self.create_message(
                    ctx, interaction, select.values[0], selection_embed, view
                )

        select.callback = selection_callback

        view = View()
        view.add_item(select)

        await ctx.reply(embed=selection_embed, view=view, mention_author=False)  # type: ignore

    async def create_message(self, ctx: Context, interaction: Interaction, media_id: int, prev_embed: Embed, old_view: View):  # type: ignore - Interaction Exists
        media_json = self.media_fetch(media_id)

        embed = Embed()
        embed.color = Color.blue()

        image_url = media_json["coverImage"]["extraLarge"]
        embed.title = media_json["title"]["romaji"]
        embed.url = media_json["siteUrl"]
        embed.description = media_json["description"]
        embed.set_thumbnail(url=image_url)

        information_string = f"Type: {media_json['type'] if media_json['format'] != 'NOVEL' else 'NOVEL'}\nStatus: {media_json['status']}\n"

        if media_json["type"] == "ANIME":
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

        discord_id = ctx.author.id

        anilist_stats = self.fetch_score(media_id, AnilistUsers.get_anilist_id(discord_id))

        if anilist_stats is not None:
            embed.add_field(
                name=f"{ctx.author.display_name} ({anilist_stats['user']['name']}) Stats",
                value=f"Status: {anilist_stats['status']}\nProgress: {anilist_stats['progress']}\nScore: {anilist_stats['score']}",
                inline=False,
            )

        embed.set_footer(text="Stats and information provided by Anilist")

        async def magnifying_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            if interaction.user == ctx.author:
                embed.set_thumbnail(url=None)  # type: ignore - None is valid
                embed.set_image(url=image_url)

                stats_button = Button(emoji="📊")
                stats_button.callback = stat_callback
                stat_view = View()
                stat_view.add_item(back_button)
                stat_view.add_item(stats_button)

                await interaction.response.edit_message(embed=embed, view=stat_view)

        async def stat_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            if interaction.user == ctx.author:
                embed.set_image(url=None)  # type: ignore - None is valid
                embed.set_thumbnail(url=image_url)

                await interaction.response.edit_message(embed=embed, view=view)

        async def back_callback(interaction: Interaction):  # type: ignore - Interaction Exosts
            if interaction.user == ctx.author:
                await interaction.response.edit_message(embed=prev_embed, view=old_view)

        magnifying_button = Button(emoji="🔍")
        magnifying_button.callback = magnifying_callback

        back_button = Button(emoji="⬅")
        back_button.callback = back_callback

        view = View()
        view.add_item(back_button)
        view.add_item(magnifying_button)

        await interaction.response.edit_message(embed=embed, view=view)  # type: ignore - View is Valid

    @commands.command(aliases=["ani"])
    async def anime(self, ctx: Context, *, arg: str = None):  # type: ignore - yes i can
        if arg is None:
            await ctx.reply("Please provide search for command")
        else:
            await self.search_embed(ctx, "ANIME", arg, None)

    @commands.command(aliases=["man"])
    async def manga(self, ctx: Context, *, arg: str = None):  # type: ignore - yes i can
        if arg is None:
            await ctx.reply("Please provide search for command")
        else:
            await self.search_embed(ctx, "MANGA", arg, "MANGA")

    @commands.command(aliases=["nov"])
    async def novel(self, ctx: Context, *, arg: str = None):  # type: ignore - yes i can
        if arg is None:
            await ctx.reply("Please provide search for command")
        else:
            await self.search_embed(ctx, "MANGA", arg, "NOVEL")

    @commands.command(aliases=["acc"])
    async def account(self, ctx: Context):
        await self.create_setup_embed(ctx)

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs["ENABLE_ANILIST"] and configs["ANILIST_URL"]


async def setup(bot: ManChanBot):
    if Anilist.is_enabled(bot.configs):
        await bot.add_cog(Anilist(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.anilist")
