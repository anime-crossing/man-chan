from __future__ import annotations

from typing import TYPE_CHECKING, cast

from disnake.ui import Button, Modal, Select, View

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Union

    from disnake import Embed, Interaction, Member, User
    from disnake.channel import DMChannel, GroupChannel
    from disnake.guild import GuildMessageable
    from disnake.ui import Item, UIComponent

    from utils.distyping import Callback, Config, Context, ModalCallback


class ServiceBase:
    def __init__(self, ctx: Context, configs: Config = {}):
        self._ctx = ctx
        self.configs = configs

    @property
    def author(self) -> Union[User, Member]:
        return self._ctx.author

    @property
    def author_id(self) -> int:
        return self._ctx.author.id

    @property
    def author_name(self) -> str:
        return self._ctx.author.display_name

    @property
    def channel(self) -> GuildMessageable | DMChannel | GroupChannel:
        return self._ctx.channel

    @property
    def ctx(self) -> Context:
        return self._ctx


class MessageBase(ServiceBase):
    def __init__(
        self,
        ctx: Context,
        configs: Config = {},
        cur_embed: Optional[Embed] = None,
        cur_view: Optional[CustomView] = None,
        cur_select: Optional[CustomSelect] = None,
        prev_message: Optional[MessageBase] = None,
        items: List[Button[Any]] = [],
        meta: Dict[str, Any] = {},
    ):
        super().__init__(ctx, configs)

        self._cur_embed = cur_embed
        self._cur_view = cur_view
        self._cur_select = cur_select
        self._prev_message = prev_message
        self._items = items
        self._meta = meta

    @property
    def view(self) -> Optional[CustomView]:
        return self._cur_view

    def set_view(self, new_view: CustomView):
        self._cur_view = new_view

    @property
    def embed(self) -> Optional[Embed]:
        return self._cur_embed

    def set_embed(self, new_embed: Embed):
        self._cur_embed = new_embed

    @property
    def previous_message(self) -> Optional[MessageBase]:
        return self._prev_message

    def set_previous_message(self, message: MessageBase):
        self._prev_message = message

    def add_button(
        self,
        button: Union[CustomButton, CustomButtonModal],
        callback: Optional[Union[Callback, CustomModal]] = None,
    ):
        if self._cur_view is None:
            raise ValueError("No view to add button in MessageBase")

        if callback is not None:
            if type(button) is CustomButton:
                button.set_callback(cast(Callback, callback))

            if type(button) is CustomButtonModal:
                button.set_modal(cast(CustomModal, callback))

        self._cur_view.add_item(button)

    def add_item(self, item: Item[Any]):
        if self.view is None:
            raise ValueError("No view to add button in MessageBase")

        self.view.add_item(item)

    async def update_message_send(
        self,
        interaction: Interaction[Any],
        new_view: Optional[CustomView] = None,
        new_embed: Optional[Embed] = None,
    ):
        if new_view is not None:
            self._cur_view = new_view

        if new_embed is not None:
            self._cur_embed = new_embed

        await interaction.response.edit_message(
            embed=self._cur_embed, view=self._cur_view
        )

    async def send(self):
        await self.channel.send(
            embed=self.embed, view=self.view  # type: ignore - Optional nulls
        )

    async def reply(self, mention_author: bool = False):
        await self.ctx.reply(
            embed=self.embed, view=self.view, mention_author=mention_author
        )

    async def exit(self, new_message: MessageBase):
        new_message.set_previous_message(self)
        await new_message.enter()

    async def enter(self) -> None:
        # Override and execute a function to initialize
        raise NotImplementedError

    def add_return_button(self):
        return_button = ReturnButton.create(self._callback_return)
        self.add_button(return_button)

    async def _callback_return(self, interaction: Interaction[Any]):
        if self._prev_message is not None:
            await self.update_message_send(
                interaction=interaction,
                new_view=self._prev_message.view,
                new_embed=self._prev_message.embed,
            )


class InteractiveBase:
    _stored_callback: Optional[Callback]

    def set_callback(self, callback: Callback):
        self._stored_callback = callback

    async def callback(self, interaction: Interaction[Any], /) -> None:
        if self._stored_callback is None:
            raise ValueError("No callback function provided")

        await self._stored_callback(interaction)


class CustomView(View):
    def add_button(
        self,
        button: CustomButton,
        callback: Optional[Callback] = None,
    ):
        if callback is not None:
            button.set_callback(callback)
        self.add_item(button)


class CustomSelect(InteractiveBase, Select):
    pass


class CustomButton(InteractiveBase, Button):
    pass


class CustomModal(Modal):
    _stored_callback: Optional[ModalCallback]

    def __init__(
        self, callback: Optional[ModalCallback], *args, **kwargs  # type: ignore
    ):
        super().__init__(*args, **kwargs)
        self._stored_callback = callback

    def set_callback(self, callback: ModalCallback, components: List[UIComponent] = []):
        self._stored_callback = callback
        if len(components) > 0:
            self.append_component(components)  # type: ignore - an inherited type

    async def callback(self, interaction: Interaction[Any], /) -> None:
        if self._stored_callback is None:
            raise ValueError("No callback function provided")

        await self._stored_callback(interaction)  # type: ignore - an inherited type


class CustomButtonModal(Button):
    def __init__(self, modal: CustomModal, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self._stored_modal = modal

    def set_modal(self, modal: CustomModal):
        self._stored_modal = modal

    async def callback(self, interaction: Interaction[Any], /) -> None:
        if self._stored_modal is None:
            raise ValueError("No modal stored in CustomButtonModal")
        await interaction.response.send_modal(self._stored_modal)


class ButtonConfirm(CustomButton):
    @classmethod
    def create(cls, callback: Callback) -> ButtonConfirm:
        this = cls(emoji="✅")
        this.set_callback(callback)
        return this


class ButtonDeny(CustomButton):
    @classmethod
    def create(cls, callback: Callback) -> ButtonDeny:
        this = cls(emoji="❌")
        this.set_callback(callback)
        return this


class ReturnButton(CustomButton):
    @classmethod
    def create(cls, callback: Callback) -> ReturnButton:
        this = cls(emoji="⬅")
        this.set_callback(callback)
        return this
