import logging
import re
from typing import Any, Dict

import requests
from disnake import Message
from disnake.ext.commands import Cog

from main import ManChanBot

from .commandbase import CommandBase


class Media_Converter(CommandBase):
    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        link = self.extract_link(message.content)
        if link:
            if "tiktok.com" in link:
                embedded_video = self.embed_tiktok(link)
                await message.edit(
                    suppress_embeds=True
                )  # Removes previous TikTok embed from context message
                await message.channel.send(f"[TikTok Link]({embedded_video})")
            elif "twitter.com" in link or "x.com" in link:
                converted_link = self.convert_twitter_link(link)
                await message.channel.send(
                    f"[Converted Twitter Link]({converted_link})"
                )

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
            return twitter_match.group(1)
        elif tiktok_match:
            return tiktok_match.group(0)
        return None

    @classmethod
    def convert_twitter_link(cls, twitter_link: str):
        converted_link = re.sub(
            r"https?://(?:www\.)?(?:twitter\.com|x\.com)",
            "https://fxtwitter.com",
            twitter_link,
        )
        return converted_link

    @classmethod
    def embed_tiktok(cls, tiktok_link: str):
        data = {"input_text": tiktok_link}

        response = requests.post(
            "https://api.quickvids.win/v1/shorturl/create", json=data
        ).json()

        return response["quickvids_url"]

    @classmethod
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs["ENABLE_CONVERTER"]


def setup(bot: ManChanBot):
    if Media_Converter.is_enabled(bot.configs):
        bot.add_cog(Media_Converter(bot))
    else:
        logging.warn("SKIPPING: cogs.xconverter")
