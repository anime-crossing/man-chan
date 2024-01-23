import logging
from typing import Any, Dict, Optional, cast

from disnake import Message, PartialEmoji, TextChannel, Embed
from disnake.raw_models import RawReactionActionEvent
from disnake.ext.commands import Cog, command

from utils.context import get_message_no_context
from utils.distyping import Context, ManChanBot


from main import ManChanBot

from .commandbase import CommandBase

class HallOfFame(CommandBase):
    @Cog.listener()
    async def on_raw_reaction_add(self, reaction: RawReactionActionEvent):
        print("reaction added")
        if reaction.emoji.name != self.star or reaction.member.bot or await self.check_reactions(self.bot, reaction):
            return
        
        message = await get_message_no_context(self.bot, reaction.channel_id, reaction.message_id)
        await self.create_post_embed(message)

    @command()
    async def setsub(self, ctx: Context, channel: TextChannel):
        # Database stuff, add channel id into database
        await ctx.channel.send(f'{channel.mention} set as submissions channel')
    
    @command()
    async def sethof(self, ctx: Context, channel: TextChannel):
        # Database stuff, add channel id into database
        await ctx.channel.send(f'{channel.mention} set as Hall-of-Fame channel')

    async def check_reactions(self, bot: ManChanBot, reaction: RawReactionActionEvent) -> bool:
        message = await get_message_no_context(bot, reaction.channel_id, reaction.message_id)
        
        if message:
            count = len([reaction for reaction in message.reactions if reaction.emoji == self.star])
            return count < self.threshold
        return False


    async def create_post_embed(self, message: Optional[Message]):
        if message:
            user = message.author

            content = f'{self.star} {message.channel.mention}'
            embed = Embed(description=message.content)

            embed.set_author(
                name = user.display_name,
                icon_url=user.display_avatar.url
            )
            embed.add_field(name="Source", value=message.jump_url, inline=False)
            return await message.channel.send(content=content, embed=embed)

    @property
    def star(self) -> PartialEmoji:
        return self.configs.get("STAR_EMOJI", "")
    
    @property
    def threshold(self) -> int:
        return self.configs.get("REACT_REQUIREMENT", 5)

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}) -> bool:
        return configs.get("ENABLE_HOF", False)
    
def setup(bot: ManChanBot):
    if HallOfFame.is_enabled(bot.configs):
        bot.add_cog(HallOfFame(bot))
    else:
        logging.warn("SKIPPING: cogs.halloffame")