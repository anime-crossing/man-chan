from typing import TYPE_CHECKING

from disnake import ButtonStyle, Color, Embed
from disnake.ui import TextInput

from ..basev2 import CustomButton, CustomButtonModal, CustomModal

if TYPE_CHECKING:
    from typing import Optional

    from utils.distyping import Callback, ModalCallback


class EmbedAccountSetup(Embed):
    @classmethod
    def create(cls, anilist_exist: bool) -> "EmbedAccountSetup":
        if anilist_exist:
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
        self.description = "Please re-run the command and be aware of any spelling mistakes.  Enter username as seen on Anilist"
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
        self.description = (
            "Account not Linked, rechoose the name when re-running `!acc`"
        )
        self.set_thumbnail(url=None)


class ModalAccountSetupInit(CustomModal):
    @classmethod
    def create(
        cls, user_id: str, callback: Optional[ModalCallback]
    ) -> "ModalAccountSetupInit":
        answer_input: TextInput = TextInput(
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
        return cls(
            callback=callback,
            label="Remove Account",
            emoji="🗑️",
            style=ButtonStyle.danger,
        )


class ButtonAccountConfirm(CustomButton):
    @classmethod
    def create(cls, callback: Callback) -> "ButtonAccountConfirm":
        return cls(emoji="✅", callback=callback)


class ButtonAccountDeny(CustomButton):
    @classmethod
    def create(cls, callback: Callback) -> ButtonAccountDeny:
        return cls(emoji="❌", callback=callback)
