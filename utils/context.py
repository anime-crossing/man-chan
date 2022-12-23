from discord.ext.commands.context import Context
from typing import Optional, Union
from discord import Member, Message, NotFound, HTTPException, TextChannel
import logging
from client import Client

def get_member(ctx: Context, mention: Union[int, str]) -> Optional[Member]:
    if not ctx.guild:
        return

    user_id = mention
    if type(mention) is str:
        user_id = mention.strip("<@>")

    return ctx.guild.get_member(int(user_id))

async def get_message_no_context(bot: Client, guild_id: int, channel_id: int, message_id: int) -> Optional[Message]:
    guild = bot.get_guild(guild_id)
    if not guild:
        return None

    channel = guild.get_channel(channel_id)
    if not channel:
        return None

    try:
        message = channel.fetch_message(message_id)
    except NotFound:
        return None
    except HTTPException:
        logging.warn("ERROR: HTTP Error raised when fetching a message.")
        return None

    return message