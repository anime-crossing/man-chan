from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Union, cast

from disnake import ButtonStyle, Color, Embed
from disnake.ui import Button, Select, View

from utils.config_mapper import LOGIN_INFO_TIMEOUT
from utils.tools import hex_to_rgb

from ..base import CallbackBase
from .login_base import LoginBase

if TYPE_CHECKING:
    from disnake import Interaction, Member, Message, User

    from utils.distyping import Callback


class LoginInfo(LoginBase):
    async def send_login_interaction(self):
        embed = _EmbedLoginInfo.create()
        select = (
            _SelectorLoginChoice.create()
        )  # Select Method that Creates Selection Menu for Embed

        for key, value in self.logins.items():
            emoji = value.get("emoji_text", "")
            provider = value.get("provider", "Unknown")

            embed.add_login_field(key, emoji, provider)
            select.add_key_option(key)

        view = View(timeout=20)  # Disables after 20 Second
        view.add_item(select)

        interactor = _LoginPageInteraction(
            service=self, cur_embed=embed, cur_view=view, cur_select=select
        )
        select.set_callback(interactor)
        await interactor.send()


class _LoginPageInteraction(CallbackBase):
    @property
    def logins(self) -> Dict[str, Dict[str, Any]]:
        return cast(LoginInfo, self.service).logins

    @property
    def timeout(self) -> int:
        return self.configs[LOGIN_INFO_TIMEOUT]

    async def send(self):
        self._message = await self.ctx.channel.send(
            embed=self.cur_embed, view=self.cur_view
        )

    async def callback(self, interaction: Interaction):
        """First callback when a service site is selected. Will transition to showing the site info."""
        # Interaction Author Must be Original Sender
        if interaction.user == self.author:
            # Returns list of Account Info of selection
            self._site_name = self.cur_select.values[0]
            self._login_dictionary = self.logins[self._site_name]

            await self._update_current_message()
            await interaction.response.defer()
        else:
            await self._send_invalid_message(interaction)

    async def _update_current_message(self):
        """Sends embed with selected site information."""
        selection_embed = _EmbedLoginPage.create(
            self._site_name,
            self._login_dictionary.get("description", ""),
            self.timeout,
            self._login_dictionary.get("hex", ""),
        )

        selection_link = _ButtonSiteLink.create(self._login_dictionary.get("link"))

        return_button = _ButtonReturnToMain.create()
        return_button.store_info(self.cur_embed, self.cur_view, self._message)

        password_button = _ButtonGeneratePassword.create()
        password_button.store_info(
            self.author,
            self._login_dictionary,
            self.timeout,
            self._send_invalid_message,
        )

        email_button = _ButtonGenerateEmail.create()
        email_button.store_info(
            self.author,
            self._login_dictionary,
            self.timeout,
            self._send_invalid_message,
        )

        view = View(timeout=60)
        view.add_item(return_button)
        view.add_item(selection_link)
        view.add_item(email_button)
        view.add_item(password_button)

        await self._message.edit(embed=selection_embed, view=view)

    async def _send_invalid_message(self, interaction: Interaction):
        await interaction.response.send_message(
            content="Command Ignored. User did not initiate command. Please run `!login` yourself.",
            ephemeral=True,
            delete_after=10,
        )


# Disnake UI Classes


class _EmbedLoginInfo(Embed):
    """
    Initial Page embed
    """

    @classmethod
    def create(cls) -> _EmbedLoginInfo:
        embed = cls(
            title="Various Login Information",
            description="Please do not share this information with anyone else!",
            colour=Color.blue(),
        )

        embed.set_footer(text="Email and password provided using selection menu")
        return embed

    def add_login_field(self, name: str, emoji: str, provider: str):
        self.add_field(
            name=f"{emoji} {name} {emoji}",
            value=f"Provider: {provider}",
            inline=True,
        )


class _SelectorLoginChoice(Select):
    """
    Selector menu for the initial page
    """

    @classmethod
    def create(cls) -> _SelectorLoginChoice:
        select = cls(placeholder="Choose a streaming service...")

        return select

    def add_key_option(self, key: str):
        self.add_option(label=key, emoji=None, description=f"{key} Login")

    def set_callback(self, callback_class: CallbackBase):
        self.callback = callback_class.callback


class _EmbedLoginPage(Embed):
    """
    Second page that presents menu buttons to generate login info
    """

    @classmethod
    def create(
        cls, site_name: str, description: str, timeout: int, hex: str
    ) -> _EmbedLoginPage:
        embed = cls(
            title=f"Login information for {site_name}",
            description=description,
        )

        embed.set_footer(
            text=f"Password and email will be auto deleted in {timeout} seconds"
        )

        rgb_color = hex_to_rgb(hex)
        if rgb_color is None:
            rgb_color = [0, 0, 0]
        embed.color = Color.from_rgb(*rgb_color)

        return embed


class _ButtonSiteLink(Button):
    @classmethod
    def create(cls, link: Optional[str]) -> _ButtonSiteLink:
        button = cls(label="Go to Site", url=link)

        return button


class _ButtonReturnToMain(Button):
    @classmethod
    def create(cls) -> _ButtonReturnToMain:
        button = cls(label="Return", emoji="⬅")

        return button

    def store_info(self, prev_embed: Embed, prev_view: View, message: Message):
        self.prev_embed = prev_embed
        self.prev_view = prev_view
        self.message = message

    async def callback(self, interaction: Interaction):
        await self.message.edit(embed=self.prev_embed, view=self.prev_view)
        await interaction.response.defer()


class _ButtonGeneratePassword(Button):
    @classmethod
    def create(cls) -> _ButtonGeneratePassword:
        button = cls(label="Generate Password", style=ButtonStyle.green, emoji="🔐")

        return button

    def store_info(
        self,
        author: Union[User, Member],
        login_dictionary: Dict[str, Any],
        timeout: int,
        error_message: Callback,
    ):
        self.author = author
        self.password = login_dictionary.get("password", "No password available!")
        self.timeout = timeout
        self.error_message = error_message
        return self

    async def callback(self, interaction: Interaction):
        if self.author == interaction.user:
            await interaction.response.send_message(
                content=self.password,
                ephemeral=True,
                delete_after=self.timeout,
            )
        else:
            await self.error_message(interaction)


class _ButtonGenerateEmail(Button):
    @classmethod
    def create(cls) -> _ButtonGenerateEmail:
        button = cls(label="Generate Email", style=ButtonStyle.green, emoji="👤")

        return button

    def store_info(
        self,
        author: Union[User, Member],
        login_dictionary: Dict[str, Any],
        timeout: int,
        error_message: Callback,
    ):
        self.author = author
        self.email = login_dictionary.get("email", "No email available!")
        self.timeout = timeout
        self.error_message = error_message
        return self

    async def callback(self, interaction: Interaction):
        if self.author == interaction.user:
            await interaction.response.send_message(
                content=self.email,
                ephemeral=True,
                delete_after=self.timeout,
            )
        else:
            await self.error_message(interaction)
