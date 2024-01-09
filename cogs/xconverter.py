import logging
import re
from typing import Any, Dict

from disnake import Message
from disnake.ext.commands import Cog

from main import ManChanBot

from .commandbase import CommandBase


class XConverter(CommandBase):
    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        link = self.extract_link(message.content)
        if link:
            converted_link = self.convert_twitter_link(link)
            await message.channel.send(f"Converted Twitter Link: {converted_link}")

    @classmethod
    def extract_link(cls, text: str):
        match = re.search(
            r"(https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+/status/[0-9]+(?:\?s=20)?)",
            text,
        )  # Searches for Twitter.com Link
        if match:
            return match.group(1)
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
    def is_enabled(cls, configs: Dict[str, Any] = {}):
        return configs["ENABLE_X_CONVERTER"]


def setup(bot: ManChanBot):
    if XConverter.is_enabled(bot.configs):
        bot.add_cog(XConverter(bot))
    else:
        logging.warn("SKIPPING: cogs.xconverter")
