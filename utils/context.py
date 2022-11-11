from discord.ext.commands.context import Context
from typing import Optional, Union, cast
from discord import Member, VoiceChannel

def get_member(ctx: Context, mention: Union[int, str]) -> Optional[Member]:
    if not ctx.guild:
        return

    user_id = mention
    if type(mention) is str:
        user_id = mention.strip("<@>")

    return ctx.guild.get_member(int(user_id))

def get_author_voice_channel(ctx: Context) -> Optional[VoiceChannel]:
        user_voice = cast(Member, ctx.message.author).voice

        if user_voice == None:
            return
        
        return cast(VoiceChannel, user_voice.channel)