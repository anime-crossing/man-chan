import json
import logging
from os.path import exists
from typing import Any, Dict, cast

import discord
from discord import Color, Embed, Guild
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, Select, View

from main import ManChanBot

from .commandbase import CommandBase


class Login(CommandBase):
    def get_account_info(data: Any, site: str) -> str:
        entries = list(filter(lambda entry: entry["site"] == site, data["login_info"]))
        return entries[0]

    def parse_login():
        with open("login.json", "r") as f:
            return json.load(f)

    async def create_selection_embed(
        previous: Any, selection: Any, home: Any, old_view: Any
    ):
        selection_embed = Embed()
        selection_embed.title = "Login information for " + selection["site"]
        selection_embed.color = Color.from_str(selection["hex"])
        selection_embed.description = selection["description"]
        selection_embed.set_footer(text="Password will be auto deleted in 15 seconds")

        selection_embed.add_field(
            name="Email Address", value=selection["email"], inline=True
        )

        async def return_callback(interaction):
            await previous.edit(embed=home, view=old_view)
            await interaction.response.defer()

        async def gen_callback(interaction):
            await interaction.response.send_message(
                content=selection["password"], ephemeral=True, delete_after=15
            )

        return_button = Button(label="Return", emoji="⬅")
        return_button.callback = return_callback

        selection_link = Button(label="Go to Site", url=selection["link"])

        gen_button = Button(
            label="Generate Password", style=discord.ButtonStyle.green, emoji="🔁"
        )
        gen_button.callback = gen_callback

        view = View(timeout=30)

        view.add_item(return_button)
        view.add_item(selection_link)
        view.add_item(gen_button)

        await previous.edit(embed=selection_embed, view=view)

    @commands.command()
    async def login(self, ctx: Context):
        # Create Embed with Python, reads from json config file
        config = Login.parse_login()

        embed = Embed()
        embed.title = "Various Login Information"
        embed.description = "Please do not share this information with anyone else!"
        embed.set_footer(text="Email and password provided using selection menu")
        embed.color = Color.blue()

        select = Select(  # Select Method that Creates Selection Menu for Embed
            placeholder="Choose a streaming service..."  # Placeholder Text
        )

        for i in config["login_info"]:
            embed.add_field(
                name=i["emoji_text"] + i["site"] + i["emoji_text"],
                value="Provider: " + i["provider"],
                inline=True,
            )

            select.add_option(
                label=i["site"], emoji=None, description=i["site"] + " Login"
            )

        async def my_callback(interaction):
            if (
                interaction.user == ctx.author
            ):  # Interaction Author Must be Original Sender
                account_info = Login.get_account_info(
                    config, select.values[0]
                )  # Returns list of Account Info of selection

                await Login.create_selection_embed(msg, account_info, embed, view)
                await interaction.response.defer()

        select.callback = my_callback
        view = View(timeout=15)  # Disables after  15 Second
        view.add_item(select)
        msg = await ctx.channel.send(embed=embed, view=view)

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs["ENABLE_LOGIN"]


async def setup(bot: ManChanBot):
    if Login.is_enabled(bot.configs):
        await bot.add_cog(Login(bot))
    else:
        logging.warn("SKIPPING: cogs.login")
