from typing import Any, Dict, Union

from disnake import Embed, Interaction, Member, User
from disnake.ui import Select, View

from utils.distyping import Config, Context


class ServiceBase:
    def __init__(self, ctx: Context, configs: Config = {}):
        self.ctx = ctx
        self.configs = configs

    @property
    def author(self) -> Union[User, Member]:
        return self.ctx.author


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
    def ctx(self) -> Context:
        return self.service.ctx

    @property
    def author(self) -> Union[User, Member]:
        return self.service.author

    @property
    def configs(self) -> Config:
        return self.service.configs

    async def callback(self, interaction: Interaction):
        ...

    async def send(self):
        ...
