from typing import Optional, Union

from discord import Member
from discord.ext.commands.context import Context


def get_member(ctx: Context, mention: Union[int, str]) -> Optional[Member]:
    if not ctx.guild:
        return

    user_id = mention
    if type(mention) is str:
        user_id = mention.strip("<@>")

    return ctx.guild.get_member(int(user_id))
