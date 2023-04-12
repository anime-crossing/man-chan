import logging
from typing import Any, Dict, List, Optional

import requests
from disnake import ButtonStyle, Color, Embed, Interaction
from disnake.ext import commands
from disnake.ui import Button, Modal, TextInput, View

from db.anilist_users import AnilistUsers
from service.anilist import AnilistAttributes as AniAttr
from service.anilist import AnilistService
from utils.config_mapper import ANILIST_ENABLE
from utils.context import get_member
from utils.distyping import Context, ManChanBot

from .commandbase import CommandBase


class Anilist(CommandBase):
    @commands.command(aliases=["ani"])
    async def anime(self, ctx: Context, *, arg: Optional[str] = None):
        if arg is None:
            await ctx.reply("Please provide a search query.")
        else:
            await AnilistService(ctx, self.configs).send_api_search_interaction(
                AniAttr.ANIME, arg
            )

    @commands.command(aliases=["man"])
    async def manga(self, ctx: Context, *, arg: Optional[str] = None):
        if arg is None:
            await ctx.reply("Please provide a search query.")
        else:
            await AnilistService(ctx, self.bot.configs).send_api_search_interaction(
                AniAttr.MANGA, arg, AniAttr.MANGA
            )

    @commands.command(aliases=["nov"])
    async def novel(self, ctx: Context, *, arg: Optional[str] = None):
        if arg is None:
            await ctx.reply("Please provide a search query.")
        else:
            await AnilistService(ctx, self.bot.configs).send_api_search_interaction(
                AniAttr.MANGA, arg, AniAttr.NOVEL
            )

    @commands.command(aliases=["acc"])
    async def account(self, ctx: Context):
        await AnilistService(ctx, self.bot.configs).send_account_setup()

    @commands.command(aliases=["anilb", "alb"])
    async def anime_leaderboard(self, ctx: Context):
        await AnilistService.create_leaderboard_embed(ctx)

    # Creates Account Setup Embed, Sends Modal for username entry
    async def create_setup_embed(self, ctx: Context):
        account_embed = Embed(
            title="Anilist Account Setup",
            description="Please use the button below to enter your Anilist Username",
            color=Color.blue(),
        )

        prompt = Modal(title="Enter Anilist Username")
        answer = TextInput(label="username")

        async def modal_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            await self.profile_query(ctx, interaction, answer)

        prompt.add_item(answer)
        prompt.on_submit = modal_callback

        async def entry_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            await interaction.response.send_modal(prompt)

        answer_button = Button(emoji="✏️")
        answer_button.callback = entry_callback

        view = View()
        view.add_item(answer_button)

        if AnilistUsers.get_anilist_id(ctx.author.id) is None:
            await ctx.send(embed=account_embed, view=view)  # type: ignore - view Exists
            return

        already_registered = Embed(
            title="Account already registered",
            description="To bypass and link a new account, please use the button below.",
            color=Color.blue(),
        )

        async def remove_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            already_registered.title = "Account Info Removed"
            already_registered.description = "Account Info has been removed from bot database, please re-run `!acc` to setup your account."
            already_registered.color = Color.red()

            await self.remove_anilist_id(ctx)
            await interaction.response.edit_message(embed=already_registered, view=None)  # type: ignore - View Exists

        repeat_button = Button(emoji="🔁")
        repeat_button.callback = entry_callback
        remove_button = Button(
            label="Remove Account", emoji="🗑️", style=ButtonStyle.danger
        )
        remove_button.callback = remove_callback
        registered_view = View()
        registered_view.add_item(repeat_button)
        registered_view.add_item(remove_button)

        await ctx.send(embed=already_registered, view=registered_view)  # type: ignore - view Exists

    # Used by Account Setup to obtain initial profile information
    async def profile_query(self, ctx: Context, interaction: Interaction, anilist_id: str):  # type: ignore - Interaction Exists
        anilist_url = self.configs["ANILIST_URL"]
        query = AnilistQueries.account

        variables = {"name": str(anilist_id)}

        json_response = requests.post(
            url=anilist_url, json={"query": query, "variables": variables}
        ).json()

        if "errors" in json_response:
            not_found = Embed(
                title="User not found",
                description="Please re-run the command and be aware of any spelling mistakes.  Enter username as seen on Anilist",
                color=Color.red(),
            )
            await interaction.response.send_message(embed=not_found)
            return

        account_info = json_response["data"]["User"]

        profile_embed = Embed(
            title="User Found",
            description=f"Is this your account: {account_info['name']}",
            color=Color.blue(),
            url=account_info["siteUrl"],
        )
        profile_embed.set_thumbnail(url=account_info["avatar"]["large"])

        no_button = Button(emoji="❌")
        yes_button = Button(emoji="✅")

        async def no_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            profile_embed.title = "User Not Found"
            profile_embed.url = None  # type: ignore - Takes Optional[str]
            profile_embed.color = Color.red()
            profile_embed.description = "Account not Linked, please be more specific with name when re-running `!acc`"

            profile_embed.set_thumbnail(url=None)  # type: ignore - Takes Optional[str]

            await interaction.response.edit_message(embed=profile_embed, view=None)

        async def yes_callback(interaction: Interaction):  # type: ignore - Interaction Exists
            profile_embed.title = "Profiles Linked"
            profile_embed.color = Color.green()
            profile_embed.description = "Account Info Saved to Bot."

            await interaction.response.edit_message(embed=profile_embed, view=None)
            await self.save_anilist_id(ctx, account_info["id"])

        no_button.callback = no_callback
        yes_button.callback = yes_callback

        view = View()
        view.add_item(no_button)
        view.add_item(yes_button)

        await interaction.response.edit_message(embed=profile_embed, view=view)

    # If empty, create table entry then save anilist_id to row
    async def save_anilist_id(self, ctx: Context, anilist_id: int):
        discord_id = ctx.author.id
        table_entry = AnilistUsers.get(discord_id)

        if not table_entry:
            table_entry = AnilistUsers.create(discord_id)

        table_entry.set_anilist_id(anilist_id)

    # "Removes" Anilist ID by setting it back to it's default, 0
    async def remove_anilist_id(self, ctx: Context):
        discord_id = ctx.author.id

        await self.save_anilist_id(ctx, 0)

    def update_leaderboard(self, fetch: List["AnilistUsers"]):
        anilist_url = self.configs["ANILIST_URL"]

        query = AnilistQueries.leaderboard

        for user in fetch:
            if user.anilist_id is not None:
                variables = {"id": user.anilist_id}
                stats = requests.post(
                    anilist_url, json={"query": query, "variables": variables}
                ).json()
                stats = stats["data"]["User"]["statistics"]["anime"]
                user.update_stats(stats["minutesWatched"], stats["chaptersRead"])

    async def create_leaderboard(self, ctx: Context):
        lb = Embed(title="Leaderboards")

        fetch = AnilistUsers.get_all()

        if len(fetch) == 0:
            lb.description = "No Users Associated with Bot"
            lb.color = Color.red()

            return await ctx.send(embed=lb)

        self.update_leaderboard(fetch)

        anime_field = []
        manga_field = []

        for i, users in enumerate(AnilistUsers.anime_leaderboard(), start=1):
            name = get_member(ctx, str(users.id))
            anime_field.append(
                f"{i}. {name.display_name if name else 'Unknown'} - {str(round(users.minutes_watched/float(1440), 2))} Days"
            )

        for i, users in enumerate(AnilistUsers.manga_leaderboard(), start=1):
            name = get_member(ctx, str(users.id))
            manga_field.append(
                f"{i}. {name.display_name if name else 'Unknown'} - {str(users.chapters_read)} Chapters"
            )

        lb.add_field(name="Anime", value="\n".join(anime_field), inline=True)
        lb.add_field(name="Manga", value="\n".join(manga_field), inline=True)

        await ctx.send(embed=lb)

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs.get(ANILIST_ENABLE)


def setup(bot: ManChanBot):
    if Anilist.is_enabled(bot.configs):
        bot.add_cog(Anilist(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.anilist")
