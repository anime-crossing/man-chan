from typing import Any, Union

from disnake import Embed, Member, User
from disnake.ui import Select, View

from utils.distyping import Context


class InteractionBase:
    def __init__(self, ctx: Context):
        self._ctx = ctx


class CallbackBase:
    def __init__(
        self,
        service: InteractionBase,
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

    async def send(self):
        ...
