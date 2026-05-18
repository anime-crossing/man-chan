from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Union

from disnake import Embed, Interaction, Member, User
from disnake.ui import Button, Modal, Select, TextInput, View

if TYPE_CHECKING:
    from disnake.ui import ModalTopLevelComponent

    from utils.distyping import Callback, Config, Context, ModalCallback


class ServiceBase:
    def __init__(self, ctx: "Context", configs: "Config" = {}):
        self.ctx = ctx
        self.configs = configs

    @property
    def author(self) -> Union[User, Member]:
        return self.ctx.author


class MessageBase:
    def __init__(
        self,
        service: ServiceBase,
        cur_embed: Optional[Embed] = None,
        cur_view: Optional[CustomView] = None,
        cur_select: Optional[CustomSelect] = None,
        prev_embed: Optional[Embed] = None,
        prev_view: Optional[CustomView] = None,
        prev_select: Optional[CustomSelect] = None,
        items: List[Button] = [],
        meta: Dict[str, Any] = {},
    ):
        self._service = service
        self._cur_embed = cur_embed
        self._cur_view = cur_view
        self._cur_select = cur_select
        self._prev_embed = prev_embed
        self._prev_view = prev_view
        self._prev_select = prev_select
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

    def set_embed(self, new_view: CustomView):
        self._cur_view = new_view

    @property
    def service(self) -> ServiceBase:
        return self._service

    def add_button(
        self,
        button: CustomButton,
        callback: Optional[Callback] = None,
    ):
        if callback is not None:
            button.set_callback(callback)

        if self._cur_view is None:
            raise ValueError("No view to add button in MessageBase")

        self._cur_view.add_item(button)

    async def update_embed(
        self, interaction: Interaction, new_view: Optional[CustomView] = None
    ):
        self._cur_view = new_view
        await interaction.response.edit_message(embed=self._cur_embed, view=new_view)

    # WIP
    def start(self):
        self._prestart()
        self.send()

    def enter(self):
        self._prestart()
        # self.edit()

    def _prestart(self): ...

    # ----

    async def send(self):
        self._message = await self.ctx.channel.send(
            embed=self.cur_embed, view=self.cur_view
        )


class SelectMessageBase(MessageBase):
    async def callback(self, interaction: Interaction): ...

    def set_callback_select(self):
        self._cur_select.set_callback(self.callback)


class CustomView(View):
    def add_button(
        self,
        button: CustomButton,
        callback: Optional[Callback] = None,
    ):
        if callback is not None:
            button.set_callback(callback)
        self.add_item(button)


class CustomSelect(Select):
    def set_callback(self, callback: Callable[[Interaction], Awaitable[None]]):
        self.callback = callback


class CustomButton(Button):
    _stored_callback: Optional[Callback]

    def __init__(self, callback: Optional[Callback], *args, **kwargs):
        super(*args, **kwargs)
        self._stored_callback = callback

    def set_callback(self, callback: Callback):
        self._stored_callback = callback

    async def callback(self, interaction: Interaction, /) -> None:
        if self._stored_callback is None:
            raise ValueError("No callback function provided")

        await self._stored_callback(interaction)


class CustomModal(Modal):
    _stored_callback: Optional[ModalCallback]

    def __init__(
        self,
        callback: Optional[ModalCallback],
        *args,
        **kwargs,
    ):
        super(*args, **kwargs)
        self._stored_callback = callback

    def set_callback(self, callback: ModalCallback, components: List[TextInput] = []):
        self._stored_callback = callback
        for c in components:
            self.append_component(c)

    async def callback(self, interaction: Interaction, /) -> None:
        if self._stored_callback is None:
            raise ValueError("No callback function provided")

        await self._stored_callback(interaction, self.components)


class CustomButtonModal(Button):
    def __init__(self, modal: CustomModal, *args, **kwargs):
        super(*args, **kwargs)
        self._stored_modal = modal

    async def callback(self, interaction: Interaction, /) -> None:
        if self._stored_modal is None:
            raise ValueError("No modal stored in CustomButtonModal")
        await interaction.response.send_modal(self._stored_modal)


class CallbackBase:
    """
    CallbackBase acts as a linked list of history of interactions
    a user would do as they interact with discord ui. That way
    interactions can be backtracked when needed.
    """

    def __init__(
        self,
        service: ServiceBase,
        cur_embed: Embed = None,  # type: ignore
        cur_view: View = None,  # type: ignore
        cur_select: Select[Any] = None,  # type: ignore
        prev_embed: Embed = None,  # type: ignore
        prev_view: View = None,  # type: ignore
        prev_select: Select[Any] = None,  # type: ignore
        items: List[Button] = [],
        meta: Dict[str, Any] = {},
    ):
        self.service = service

        self.cur_embed = cur_embed
        self.cur_view = cur_view
        self.cur_select = cur_select

        self.prev_embed = prev_embed
        self.prev_view = prev_view
        self.prev_select = prev_select

        self._meta = meta

    @property
    def ctx(self) -> "Context":
        return self.service.ctx

    @property
    def author(self) -> Union[User, Member]:
        return self.service.author

    @property
    def configs(self) -> "Config":
        return self.service.configs

    async def callback(self, interaction: Interaction): ...

    async def send(self):
        self._message = await self.ctx.channel.send(
            embed=self.cur_embed, view=self.cur_view
        )
