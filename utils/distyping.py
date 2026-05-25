from typing import Any, Callable, Coroutine, Dict, TypeAlias

from disnake import Interaction, ModalInteraction
from disnake.ext import commands

from main import ManChanBot

# For typing
Context: TypeAlias = commands.Context[ManChanBot]
Config: TypeAlias = Dict[str, Any]
Callback: TypeAlias = Callable[[Interaction[Any]], Coroutine[Any, Any, None]]
ModalCallback: TypeAlias = Callable[[ModalInteraction[Any]], Coroutine[Any, Any, None]]
