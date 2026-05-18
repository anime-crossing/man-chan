from typing import TYPE_CHECKING, cast

from disnake import Interaction

from db.anilist_users import AnilistUsers

from ..basev2 import MessageBase, ServiceBase
from .api import AnilistAPI, AnilistStatus
from .objects import *

if TYPE_CHECKING:
    from typing import Any, List

    from disnake.ui import TextInput

    from utils.distyping import Context


class _AccountSetupInit(MessageBase):
    async def callback_creation(
        self, interaction: Interaction[Any], modal_args: List[TextInput]
    ) -> None:
        await self.profile_query(
            self.service.ctx, interaction, anilist_id=modal_args[0]
        )

    async def callback_remove(self, interaction: Interaction[Any]) -> None:
        if self.embed is None:
            return

        cast(EmbedAccountSetup, self._cur_embed).switch_to_remove()

        await self.remove_anilist_id(ctx)
        await self.update_embed(interaction)

    async def profile_query(
        self, ctx: Context, interaction: Interaction, anilist_id: TextInput
    ):
        status, result = AnilistAPI.query_profile(str(anilist_id))
        current_embed = cast(EmbedAccountSetup, self.embed)

        if status == AnilistStatus.ERROR:
            current_embed.switch_to_error()
            await self.update_embed(interaction)
            return None

        if status == AnilistStatus.NOT_FOUND:
            current_embed.switch_to_not_found()
            await self.update_embed(interaction)
            return None

        account_info = result["data"]["User"]  # type: ignore

        current_embed.switch_to_found(
            account_info["name"],
            account_info["siteUrl"],
            account_info["avatar"]["large"],
        )

        confirm_view = CustomView()
        confirm_view.add_button(ButtonAccountDeny.create(self.callback_deny))
        confirm_view.add_button(ButtonAccountConfirm.create(self.callback_confirm))
        await self.update_embed(interaction, confirm_view)

    async def callback_confirm(self, interaction: Interaction):
        cast(EmbedAccountSetup, self.embed).switch_to_linked()
        await self.save_anilist_id(ctx, account_info["id"])
        await self.update_embed(interaction)

    async def callback_deny(self, interaction: Interaction):
        cast(EmbedAccountSetup, self.embed).switch_to_rejected()
        await self.update_embed(interaction)


class AnilistInteraction(ServiceBase):

    async def setup_account(self):
        anilist_exist = AnilistUsers.get_anilist_id(self.author.id) is not None

        account_setup = _AccountSetupInit(
            service=self,
            cur_embed=EmbedAccountSetup.create(anilist_exist),
            cur_view=CustomView(),
        )

        input_modal = ModalAccountSetupInit.create(str(self.author.id))
        input_modal.set_callback(account_setup.callback_creation)
        modal_button = ButtonAccountSetupInit.create(anilist_exist, input_modal)

        account_setup.add_button(
            ButtonAccountSetupInit.create(anilist_exist, input_modal)
        )

        # Anilist not connected yet. Only provider registration
        if not anilist_exist:
            account_setup.send()
            return None

        # Anilist already connected. Offer changing name or removing
        # Changing name already done in ButtonAccountSetupInit
        account_setup.add_button(
            ButtonAccountSetupRemove.create(account_setup.callback_remove)
        )

        account_setup.send()
