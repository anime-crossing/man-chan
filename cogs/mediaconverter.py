import logging
import re
from typing import Any, Dict, Optional

import requests
from disnake import Message, Reaction, User
from disnake.ext.commands import Cog

from main import ManChanBot

from .commandbase import CommandBase


class MediaConverter(CommandBase):
    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        link_type, link_url = self.extract_link(message.content)
        if link_type:
            description = ""
            if link_type == "tiktok":
                embedded_video = self.embed_tiktok(link_url)
                description = f"[TikTok Link]({embedded_video})"

                await message.edit(
                    suppress_embeds=True
                )  # Removes previous embed from context message
                await message.reply(content=description, mention_author=False)

            elif link_type == "twitter":
                return await self.mark_twitter_post(message)

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: User):
        if (
            reaction.emoji != "📹"
            or user.bot
            or reaction.count > 2
            or not self.extract_link(reaction.message.content)
        ):
            return

        message = reaction.message
        if not message.embeds:
            await message.reply(content="Dickhead this already sent")
            return  # this assumes that the message embeds have already been surpressed.
        link = self.convert_twitter_link(message.content)
        await message.edit(suppress_embeds=True)
        await message.reply(content=f"[Twitter Link]({link})", mention_author=False)

    @classmethod
    def extract_link(cls, text: str):
        twitter_match = re.search(
            r"(https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+/status/[0-9]+(?:\?s=20)?)",
            text,
        )
        tiktok_match = re.search(
            r"https?://(?:www\.)?tiktok\.com/[a-zA-Z0-9_]+/[a-zA-Z0-9_]+",
            text,
        )
        if twitter_match:
            return "twitter", twitter_match.group(1)
        elif tiktok_match:
            return "tiktok", tiktok_match.group(0)
        return None, None

    @classmethod
    async def mark_twitter_post(cls, message: Message):
        return await message.add_reaction("📹")

    @classmethod
    def convert_twitter_link(cls, twitter_link: Optional[str]):
        if twitter_link:
            converted_link = re.sub(
                r"https?://(?:www\.)?(?:twitter\.com|x\.com)",
                "https://fxtwitter.com",
                twitter_link,
            )
            return converted_link
        return None

    @classmethod
    def embed_tiktok(cls, tiktok_link: Optional[str]):
        if tiktok_link:
            data = {"input_text": tiktok_link}

            response = requests.post(
                "https://api.quickvids.win/v1/shorturl/create", json=data
            ).json()

            return response["quickvids_url"]
        return None

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs.get("ENABLE_MEDIA_LINK_CONVERTER", False)


def setup(bot: ManChanBot):
    if MediaConverter.is_enabled(bot.configs):
        bot.add_cog(MediaConverter(bot))
    else:
        logging.warn("SKIPPING: cogs.mediaconverter")
