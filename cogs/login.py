import json
import logging
from pathlib import Path
from typing import Any, Dict

import discord
from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, Select, View                 #type: ignore

from main import ManChanBot

from .commandbase import CommandBase

class Login(CommandBase):
    def open_json():                                        # type: ignore
        # Checks to see if File Exists
        path = "login.json"
        obj = Path(path)

        if obj.exists():
            try:
                # Check to see if JSON File opens properly
                with open(path) as f:
                    return json.loads(f.read())
                # Error decoding JSON File, File Invalid
            except json.decoder.JSONDecodeError:
                print("JSON File is not valid")
                return
                # Opening Error
            except IOError:
                print(f"Error opening {path}")
                return
        else:
            return

    def get_account_info(self, data: Any, site: str) -> str:
        entries = list(filter(lambda entry: entry["site"] == site, data["login_info"]))
        return entries[0]

    async def create_selection_embed(self,
        previous: Any, selection: Any, home: Any, old_view: Any
    ):
        selection_embed = Embed()
        selection_embed.title = "Login information for " + selection["site"]
        selection_embed.color = Color.from_str(selection["hex"])        # type: ignore
        selection_embed.description = selection["description"]
        selection_embed.set_footer(text="Password will be auto deleted in 15 seconds")

        async def return_callback(interaction: Any):
            await previous.edit(embed=home, view=old_view)
            await interaction.response.defer()

        async def gen_callback(interaction: Any):
            await interaction.response.send_message(
                content=selection["password"], ephemeral=True, delete_after=15
            )

        async def email_callback(interaction: Any):
            await interaction.response.send_message(
                content=selection["email"], ephemeral=True, delete_after=15
            )

        return_button = Button(label="Return", emoji="⬅")
        return_button.callback = return_callback

        selection_link = Button(label="Go to Site", url=selection["link"])

        gen_button = Button(
            label="Generate Password", style=discord.ButtonStyle.green, emoji="🔐"  #type: ignore
        )
        gen_button.callback = gen_callback

        email_button = Button(
            label="Generate Email", style=discord.ButtonStyle.green, emoji="👤"     #type: ignore
        )
        email_button.callback = email_callback

        view = View(timeout=60)

        view.add_item(return_button)
        view.add_item(selection_link)
        view.add_item(email_button)
        view.add_item(gen_button)

        await previous.edit(embed=selection_embed, view=view)

    @commands.command()
    async def login(self, ctx: Context):
        # Create Embed with Python, reads from json config file
        config = Login.open_json()

        if config is None:
            embed = Embed()
            embed.title = "JSON File Broken"
            embed.description = "Please contact Bot Admins to Fix"
            embed.color = Color.red()
            await ctx.send(embed=embed)
            return

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

        async def my_callback(interaction: Any):
            if (
                interaction.user == ctx.author
            ):  # Interaction Author Must be Original Sender
                account_info = Login.get_account_info(self,
                    config, select.values[0]
                )  # Returns list of Account Info of selection

                await Login.create_selection_embed(self, msg, account_info, embed, view)
                await interaction.response.defer()

        select.callback = my_callback
        view = View(timeout=20)  # Disables after 20 Second
        view.add_item(select)
        msg = await ctx.channel.send(embed=embed, view=view) # type: ignore

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        if not Login.open_json():
            return False
        return configs["ENABLE_LOGIN"]


async def setup(bot: ManChanBot):
    if Login.is_enabled(bot.configs):
        await bot.add_cog(Login(bot)) # type: ignore
    else:
        logging.warn("SKIPPING: cogs.login")
