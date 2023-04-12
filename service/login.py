from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from disnake import ButtonStyle, Color, Embed
from disnake.ui import Button, Select, View

from utils.config_mapper import LOGIN_FILE_PATH
from utils.tools import hex_to_rgb

if TYPE_CHECKING:
    from disnake import Interaction, Member, User

    from utils.distyping import Context


class LoginService:
    def __init__(self, ctx: Context, path: Optional[str], timeout: int):
        self._ctx = ctx
        self._timeout = timeout
        self.open_json(path)

    @classmethod
    def open_json(cls, path: Optional[str]) -> bool:
        # Checks to see if File Exists
        if path is None:
            return False

        file = Path(path)
        if file.exists() and file.is_file():
            try:
                # Check to see if JSON File opens properly
                with file.open(encoding="utf-8") as f:
                    cls._logins: Dict[str, Dict] = json.loads(f.read())
                    return True
            except json.decoder.JSONDecodeError:
                logging.warn("JSON File is not valid")
            except IOError:
                logging.warn(f"Error opening {LOGIN_FILE_PATH}")
        cls._logins = dict()
        return False

    def create_broken_file_error_embed(self):
        embed = Embed()
        embed.title = "JSON File Broken"
        embed.description = "Please contact Bot Admins to Fix"
        embed.color = Color.red()

        return embed

    def is_login_empty(self) -> bool:
        return len(self._logins) < 1

    async def send_login_interaction(self):
        embed = Embed()
        embed.title = "Various Login Information"
        embed.description = "Please do not share this information with anyone else!"
        embed.set_footer(text="Email and password provided using selection menu")
        embed.color = Color.blue()

        select = Select(  # Select Method that Creates Selection Menu for Embed
            placeholder="Choose a streaming service..."
        )

        for key, value in self._logins.items():
            emoji = value.get("emoji_text", "")
            provider = value.get("provider", "Unknown")

            embed.add_field(
                name=f"{emoji} {key} {emoji}",
                value=f"Provider: {provider}",
                inline=True,
            )

            select.add_option(label=key, emoji=None, description=f"{key} Login")

        view = View(timeout=20)  # Disables after 20 Second
        view.add_item(select)

        await _Login_Info(self, embed, view, select).send()


class _Login_Info:
    def __init__(
        self,
        service: LoginService,
        old_embed: Embed,
        old_view: View,
        select: Select[Any],
    ):
        self._service = service
        self._old_embed = old_embed
        self._old_view = old_view
        self._select = select

    @property
    def _ctx(self) -> Context:
        return self._service._ctx

    @property
    def _author(self) -> Union[User, Member]:
        return self._service._ctx.author

    @property
    def _logins(self) -> Dict[str, Dict]:
        return self._service._logins

    @property
    def _timeout(self) -> int:
        return self._service._timeout

    async def send(self):
        self._select.callback = self._callback_login_option_selected
        self._message = await self._ctx.channel.send(
            embed=self._old_embed, view=self._old_view
        )

    async def _callback_login_option_selected(self, interaction: Interaction):
        """First callback when a service site is selected. Will transition to showing the site info."""
        # Interaction Author Must be Original Sender
        if interaction.user == self._author:
            # Returns list of Account Info of selection
            site_name = self._select.values[0]
            self._login_dictionary = self._logins[site_name]

            await self._create_selection_embed(site_name)
            await interaction.response.defer()
        else:
            await self.send_invalid_message(interaction)

    async def _create_selection_embed(self, site_name: str):
        """Sends embed with selected site information."""
        selection_embed = Embed()
        selection_embed.title = f"Login information for {site_name}"
        selection_embed.description = self._login_dictionary.get("description", "")
        selection_embed.set_footer(
            text=f"Password will be auto deleted in {self._timeout} seconds"
        )
        selection_link = Button(
            label="Go to Site", url=self._login_dictionary.get("link")
        )

        rgb_color = hex_to_rgb(self._login_dictionary.get("hex", ""))
        if rgb_color is None:
            rgb_color = [0, 0, 0]
        selection_embed.color = Color.from_rgb(*rgb_color)

        # Return callback button
        return_button = Button(label="Return", emoji="⬅")
        return_button.callback = self._callback_return_to_main_login

        # Password callback button
        password_button = Button(
            label="Generate Password", style=ButtonStyle.green, emoji="🔐"
        )
        password_button.callback = self._callback_show_password

        # Email callback button
        email_button = Button(
            label="Generate Email", style=ButtonStyle.green, emoji="👤"
        )
        email_button.callback = self._callback_show_email

        view = View(timeout=60)
        view.add_item(return_button)
        view.add_item(selection_link)
        view.add_item(email_button)
        view.add_item(password_button)

        await self._message.edit(embed=selection_embed, view=view)

    async def _callback_return_to_main_login(self, interaction: Interaction):
        await self._message.edit(embed=self._old_embed, view=self._old_view)
        await interaction.response.defer()

    async def _callback_show_password(self, interaction: Interaction):
        if self._author == interaction.user:
            await interaction.response.send_message(
                content=self._login_dictionary.get(
                    "password", "No password available!"
                ),
                ephemeral=True,
                delete_after=self._timeout,
            )
        else:
            await self.send_invalid_message(interaction)

    async def _callback_show_email(self, interaction: Interaction):
        if self._author == interaction.user:
            await interaction.response.send_message(
                content=self._login_dictionary.get("email", "No email available!"),
                ephemeral=True,
                delete_after=self._timeout,
            )
        else:
            await self.send_invalid_message(interaction)

    async def send_invalid_message(self, interaction: Interaction):
        await interaction.response.send_message(
            content="Command Ignored. User did not initiate command. Please run `!login` yourself.",
            ephemeral=True,
            delete_after=10,
        )
