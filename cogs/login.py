import json
import logging
from pathlib import Path
from typing import Any, Dict

from discord import ButtonStyle  # type: ignore - Button Style Exists but PyLance Yells
from discord import Interaction  # type: ignore - Interaction Exists but PyLance Yells
from discord import Color, Embed, Message
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.ui import Button, Select, View  # type: ignore

from main import ManChanBot

from .commandbase import CommandBase


class Login(CommandBase):
    @staticmethod
    def open_json():
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
                logging.warn("JSON File is not valid")
                # Opening Error
            except IOError:
                logging.warn(f"Error opening {path}")

    async def send_invalid_message(self, interaction: Interaction):  # type: ignore - Interaction Exists
        await interaction.response.send_message(
            content="Command Ignored. User did not initiate command. Please run `!login` yourself.",
            ephemeral=True,
            delete_after=10,
        )

    async def create_selection_embed(
        self, current_message: Message, site_name: str, login_dictionary: Dict[str, str], old_embed: Embed, old_view: View, ctx: Context  # type: ignore - Pylance doesn't know what a view is
    ):
        selection_embed = Embed()
        selection_embed.title = "Login information for " + site_name
        selection_embed.color = Color.from_str(login_dictionary["hex"])  # type: ignore
        selection_embed.description = login_dictionary["description"]
        selection_embed.set_footer(text="Password will be auto deleted in 15 seconds")

        async def return_callback(interaction: Interaction):  # type: ignore - Interaction exists...
            await current_message.edit(embed=old_embed, view=old_view)  # type: ignore - Pylance doesn't know what a view is
            await interaction.response.defer()

        async def password_callback(interaction: Interaction):  # type: ignore - Interaction exists...
            if ctx.author == interaction.user:
                await interaction.response.send_message(
                    content=login_dictionary["password"],
                    ephemeral=True,
                    delete_after=15,
                )
            else:
                await self.send_invalid_message(interaction)

        async def email_callback(interaction: Interaction):  # type: ignore - Interaction exists...
            if ctx.author == interaction.user:
                await interaction.response.send_message(
                    content=login_dictionary["email"], ephemeral=True, delete_after=15
                )
            else:
                await self.send_invalid_message(interaction)

        return_button = Button(label="Return", emoji="⬅")
        return_button.callback = return_callback

        selection_link = Button(label="Go to Site", url=login_dictionary["link"])

        password_button = Button(
            label="Generate Password", style=ButtonStyle.green, emoji="🔐"  # type: ignore
        )
        password_button.callback = password_callback

        email_button = Button(
            label="Generate Email", style=ButtonStyle.green, emoji="👤"  # type: ignore
        )
        email_button.callback = email_callback

        view = View(timeout=60)

        view.add_item(return_button)
        view.add_item(selection_link)
        view.add_item(email_button)
        view.add_item(password_button)

        await current_message.edit(embed=selection_embed, view=view)  # type: ignore - Pylance doesn't know what a view is

    @commands.command()
    async def login(self, ctx: Context):
        # Create Embed with Python, reads from json config file
        config = Login.open_json()
        embed = Embed()

        if config is None:
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

        for key, value in config.items():
            embed.add_field(
                name=value["emoji_text"] + key + value["emoji_text"],
                value="Provider: " + value["provider"],
                inline=True,
            )

            select.add_option(label=key, emoji=None, description=key + " Login")

        async def my_callback(interaction: Interaction):  # type: ignore - Interaction exists...
            # Interaction Author Must be Original Sender
            if interaction.user == ctx.author:
                # Returns list of Account Info of selection
                account_info = config[select.values[0]]

                await self.create_selection_embed(
                    message, select.values[0], account_info, embed, view, ctx
                )
                await interaction.response.defer()
            else:
                await self.send_invalid_message(interaction)

        select.callback = my_callback
        view = View(timeout=20)  # Disables after 20 Second
        view.add_item(select)
        message = await ctx.channel.send(embed=embed, view=view)  # type: ignore

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs["ENABLE_LOGIN"] and Login.open_json()


async def setup(bot: ManChanBot):
    if Login.is_enabled(bot.configs):
        await bot.add_cog(Login(bot))  # type: ignore
    else:
        logging.warn("SKIPPING: cogs.login")
