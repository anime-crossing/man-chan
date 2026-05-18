from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine, Dict, List

    from disnake import Interaction
    from disnake.ext import commands
    from disnake.ui import UIComponent

    from main import ManChanBot

# For typing
Context: TypeAlias = commands.Context[ManChanBot]
Config: TypeAlias = Dict[str, Any]
Callback: TypeAlias = Callable[[Interaction[Any]], Coroutine[Any, Any, None]]
ModalCallback: TypeAlias = Callable[
    [Interaction[Any], List[UIComponent]], Coroutine[Any, Any, None]
]
