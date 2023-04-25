from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional, Union, cast

from disnake import HTTPException, NotFound, TextChannel

if TYPE_CHECKING:
    from disnake import Member, Message

    from .distyping import Context, ManChanBot


def get_member(ctx: Context, mention: Union[int, str]) -> Optional[Member]:
    if not ctx.guild:
        return

    user_id = mention
    if type(mention) is str:
        user_id = mention.strip("<@>")

    return ctx.guild.get_member(int(user_id))


async def get_message_no_context(
    bot: ManChanBot, channel_id: int, message_id: int
) -> Optional[Message]:
    if not (channel_id and message_id):
        return

    channel = cast(TextChannel, bot.get_channel(channel_id))
    if not channel:
        return None

    try:
        message = await channel.fetch_message(message_id)
    except NotFound:
        return None
    except HTTPException:
        logging.warn("ERROR: HTTP Error raised when fetching a message.")
        return None

    return message
