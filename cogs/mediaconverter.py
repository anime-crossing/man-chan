import logging
from typing import Any, Callable, Dict

from disnake import Message, Reaction, User
from disnake.ext.commands import Cog

from main import ManChanBot
from utils import LinkType, MediaLinkFormatter

from .commandbase import CommandBase


class MediaConverter(CommandBase):
    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        link_type, link_url = MediaLinkFormatter.detect_link(message.content)

        if not (link_type and link_url):
            return

        if link_type == LinkType.TIKTOK:
            await self._send_embed(
                link_url, "TikTok Link", message, MediaLinkFormatter.embed_tiktok
            )

        if link_type == LinkType.TWITTER:
            return await self.mark_post_emoji(message)

        if link_type == LinkType.INSTAGRAM:
            replied_message = await self._send_embed(
                link_url, "Instagram Link", message, MediaLinkFormatter.embed_instagram
            )
            return await self.mark_post_emoji(replied_message)

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: User):
        if reaction.emoji != "📹" or user.bot or reaction.count > 2:
            return

        message = reaction.message
        if not message.embeds:
            return  # this assumes that the message embeds have already been surpressed.

        link_type, link_url = MediaLinkFormatter.detect_link(reaction.message.content)
        if not (link_type and link_url):
            return

        if link_type == LinkType.TWITTER:
            await self._send_embed(
                link_url, "Twitter Link", message, MediaLinkFormatter.embed_twitter
            )

        if link_type == LinkType.INSTAGRAM:
            await self._send_embed(
                link_url,
                "Instagram Download",
                message,
                MediaLinkFormatter.embed_instagram_dd,
                suppress=False,
            )

    @classmethod
    async def mark_post_emoji(cls, message: Message):
        return await message.add_reaction("📹")

    async def _send_embed(
        self,
        link_url: str,
        link_desc: str,
        message: Message,
        embed_func: Callable[[str], str],
        suppress: bool = True,
    ) -> Message:
        embedded_video = embed_func(link_url)
        description = f"[{link_desc}]({embedded_video})"

        if suppress:
            await message.edit(
                suppress_embeds=True
            )  # Removes previous embed from context message

        replied_message = await message.reply(content=description, mention_author=False)
        return replied_message

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs.get("ENABLE_MEDIA_LINK_CONVERTER", False)


def setup(bot: ManChanBot):
    if MediaConverter.is_enabled(bot.configs):
        bot.add_cog(MediaConverter(bot))
    else:
        logging.warn("SKIPPING: cogs.mediaconverter")
