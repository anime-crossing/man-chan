from __future__ import annotations

from typing import TYPE_CHECKING

from disnake import ButtonStyle, Color, Embed
from disnake.ui import TextInput

from ..basev2 import CustomButton, CustomButtonModal, CustomModal, CustomSelect

if TYPE_CHECKING:
    from typing import List, Optional

    from utils.distyping import Callback, ModalCallback


class EmbedAccountSetup(Embed):
    @classmethod
    def create(cls, anilist_exist: bool) -> EmbedAccountSetup:
        if not anilist_exist:
            return cls(
                title="Anilist Account Setup",
                description="Please use the button below to enter your Anilist Username",
                color=Color.blue(),
            )

        return cls(
            title="Account already registered",
            description="To bypass and link a new account, please use the button below.",
            color=Color.blue(),
        )

    def switch_to_remove(self):
        self.title = "Account Info Removed"
        self.description = "Account Info has been removed from bot database, please re-run `!aniacc` to setup your account."
        self.colour = Color.red()

    def switch_to_error(self):
        self.title = "Error Fetching Account"
        self.description = "Internal error occured. Please contact the devs"
        self.colour = Color.red()

    def switch_to_not_found(self):
        self.title = "User not found"
        self.description = "Please re-run the command and be aware of any spelling mistakes. Enter username as seen on Anilist"
        self.colour = Color.red()

    def switch_to_found(self, account_name: str, account_url: str, avatar: str):
        self.title = "User Found"
        self.description = f"Is this your account: {account_name}"
        self.colour = Color.blue()
        self.url = account_url
        self.set_thumbnail(avatar)

    def switch_to_linked(self):
        self.title = "Profiles Linked"
        self.color = Color.green()
        self.description = "Account Info Saved to Bot."

    def switch_to_rejected(self):
        self.title = "User Not Linked"
        self.url = None
        self.color = Color.red()
        self.description = "Account not Linked, please try again."
        self.set_thumbnail(url=None)


class ModalAccountSetupInit(CustomModal):
    @classmethod
    def create(
        cls, user_id: str, callback: Optional[ModalCallback] = None
    ) -> ModalAccountSetupInit:
        answer_input = TextInput(
            label="username", custom_id=f"anilist-username-input-{user_id}"
        )
        return cls(callback, title="Enter Anilist Username", components=[answer_input])


class ButtonAccountSetupInit(CustomButtonModal):
    @classmethod
    def create(
        cls, anilist_exist: bool, callback_modal: CustomModal
    ) -> "ButtonAccountSetupInit":
        emoji = "🔁" if anilist_exist else "✏️"
        return cls(modal=callback_modal, emoji=emoji)


class ButtonAccountSetupRemove(CustomButton):
    @classmethod
    def create(cls, callback: Callback) -> ButtonAccountSetupRemove:
        this = cls(
            label="Remove Account",
            emoji="🗑️",
            style=ButtonStyle.danger,
        )
        this.set_callback(callback)
        return this


class EmbedSearch(Embed):
    @classmethod
    def create(cls) -> EmbedSearch:
        return cls()

    def switch_to_error(self):
        self.title = "Internal error"
        self.description = "Internal error occured. Please contact the devs"
        self.colour = Color.red()

    def switch_to_not_found(self):
        self.title = "Media not found"
        self.description = "Nothing found in Anilist. Recheck spelling and refine your search parameters to try again."
        self.colour = Color.purple()

    def switch_to_found_list(self, search_number: int, field_value: str):
        self.title = "Search Results"
        self.description = "Please select the entry using the menu below."
        self.colour = Color.blue()

        self.add_field(
            name=f"Showing entries of 1-{search_number} of {search_number}",
            value=field_value,
            inline=True,
        )


class SelectSearchOption(CustomSelect):
    @classmethod
    def create(cls) -> CustomSelect:
        return cls(placeholder="Select an entry")

    def put_option(self, num: int, title: str, id: str, staff: str):
        self.add_option(label=f"{num}. {title}", value=id, description=staff)


class EmbedAniInfo(Embed):
    @classmethod
    def create(cls) -> EmbedAniInfo:
        return cls(color=Color.blue())

    def switch_to_error(self):
        self.title = "Internal error"
        self.description = "Internal error occured. Please contact the devs"
        self.colour = Color.red()

    def set_info(
        self,
        title: str,
        url: str,
        description: str,
        info: str,
        thumbnail: str,
        genres: List[str],
    ):
        self.title = title
        self.url = url
        self.description = description

        self.set_thumbnail(thumbnail)

        self.add_field(name="Information", value=info, inline=True)
        self.add_field(name="Genre", value=("\n".join(genres)), inline=True)

        self.set_footer(text="Stats and information provided by Anilist")

        self._stored_thumbnail = thumbnail

    def add_score(
        self,
        discord_name: str,
        anilist_name: str,
        status: str,
        progress: str,
        score: str,
    ):
        self.add_field(
            name=f"{discord_name} ({anilist_name}) Stats",
            value=f"Status: {status}\nProgress: {progress}\nScore: {score}",
            inline=False,
        )

    def magnify_image(self):
        self.set_thumbnail(url=None)
        self.set_image(url=self._stored_thumbnail)

    def minify_image(self):
        self.set_thumbnail(url=self._stored_thumbnail)
        self.set_image(url=None)


class ButtonMagnifier(CustomButton):
    @classmethod
    def create(cls) -> ButtonMagnifier:
        return cls(emoji="🔍")


class ButtonStatsSwitch(CustomButton):
    @classmethod
    def create(cls) -> ButtonStatsSwitch:
        return cls(emoji="📊")


class EmbedLeaderboard(Embed):
    @classmethod
    def create(cls) -> EmbedLeaderboard:
        return cls(title="Leaderboards")

    def switch_to_empty(self):
        self.description = "No Users Associated with Bot"
        self.colour = Color.red()

    def not_found_error(self):
        self.set_footer(text="Note: Could not refresh your profile stats - Not found")

    def not_general_error(self):
        self.set_footer(
            text="Note: Could not refresh your profile stats - Internal error"
        )
