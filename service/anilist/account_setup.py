from __future__ import annotations

from typing import TYPE_CHECKING, cast

from db.anilist_users import AnilistUsers
from utils.tools import dig, empty_or_default

from ..basev2 import ButtonConfirm, ButtonDeny, CustomView, MessageBase
from .api import AnilistAPI, AnilistStatus
from .objects import *

if TYPE_CHECKING:
    from typing import Any

    from disnake import Interaction, ModalInteraction

    from utils.distyping import Context


class AccountSetup(MessageBase):
    async def setup_account(self):
        anilist_exist = AnilistUsers.get_anilist_id(self.author.id) is not None

        self.set_embed(EmbedAccountSetup.create(anilist_exist))
        self.set_view(CustomView())

        self._input_modal = ModalAccountSetupInit.create(str(self.author.id))
        self._input_modal.set_callback(self._callback_creation)

        self.add_button(ButtonAccountSetupInit.create(anilist_exist, self._input_modal))

        # Anilist not connected yet. Only provider registration
        if not anilist_exist:
            return await self.send()

        # Anilist already connected. Offer changing name or removing
        # Changing name already done in ButtonAccountSetupInit
        self.add_button(ButtonAccountSetupRemove.create(self._callback_remove))

        return await self.send()

    async def _profile_query(
        self, ctx: Context, interaction: Interaction[Any], anilist_id: Optional[str]
    ):
        current_embed = cast(EmbedAccountSetup, self.embed)

        if anilist_id is None:
            current_embed.switch_to_not_found()
            await self.update_message_send(interaction)
            return None

        status, result = AnilistAPI.query_profile(anilist_id)

        if status == AnilistStatus.NOT_FOUND:
            current_embed.switch_to_not_found()
            await self.update_message_send(interaction)
            return None

        if status == AnilistStatus.ERROR or result is None:
            current_embed.switch_to_error()
            await self.update_message_send(interaction)
            return None

        account_info = dig(result, "data", "User")
        if account_info is None:
            current_embed.switch_to_error()
            await self.update_message_send(interaction)
            return None

        acc_id = empty_or_default(dig(account_info, "id"))
        acc_name = empty_or_default(dig(account_info, "name"))
        acc_url = empty_or_default(dig(account_info, "siteUrl"))
        acc_avatar = empty_or_default(dig(account_info, "avatar", "large"))

        if acc_id is None:
            current_embed.switch_to_error()
            await self.update_message_send(interaction)
            return None

        current_embed.switch_to_found(
            acc_name,
            acc_url,
            acc_avatar,
        )

        self._anilist_id = acc_id

        confirm_view = CustomView()
        confirm_view.add_button(ButtonDeny.create(self._callback_deny))
        confirm_view.add_button(ButtonConfirm.create(self._callback_confirm))
        await self.update_message_send(interaction, confirm_view)

    async def _callback_creation(self, interaction: ModalInteraction[Any]) -> None:
        anilist_name = None
        interact_values = list(interaction.text_values.values())
        if len(interact_values) > 0:
            anilist_name = interact_values[0]

        await self._profile_query(self.ctx, interaction, anilist_id=anilist_name)

    async def _callback_remove(self, interaction: Interaction[Any]) -> None:
        if self.embed is None:
            return

        cast(EmbedAccountSetup, self._cur_embed).switch_to_remove()

        self.save_anilist_user(removing=True)
        self.set_view(CustomView())  # Remove buttons
        await self.update_message_send(interaction)

    async def _callback_confirm(self, interaction: Interaction[Any]):
        cast(EmbedAccountSetup, self.embed).switch_to_linked()
        self.save_anilist_user(anilist_id=self._anilist_id)
        self.set_view(CustomView())  # Remove buttons
        await self.update_message_send(interaction)

    async def _callback_deny(self, interaction: Interaction[Any]):
        cast(EmbedAccountSetup, self.embed).switch_to_rejected()
        self.set_view(CustomView())  # Remove buttons
        self.add_button(ButtonAccountSetupInit.create(False, self._input_modal))
        await self.update_message_send(interaction)

    def save_anilist_user(
        self, anilist_id: Optional[int] = None, removing: bool = False
    ) -> AnilistUsers:
        table_entry = AnilistUsers.get(self.author_id)
        new_ani_id = None if removing or anilist_id is None else anilist_id

        if not table_entry:
            return AnilistUsers.create(self.author_id, anilist_id=new_ani_id)

        return table_entry.set_anilist_id(new_ani_id)
