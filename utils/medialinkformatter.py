import re
from enum import Enum
from typing import Optional, Tuple

import requests


class LinkType(Enum):
    TWITTER = 1
    TIKTOK = 2
    INSTAGRAM = 3


class MediaLinkFormatter:
    re_link = r"https?://"
    re_twitter = r"(https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+/status/[0-9]+(?:\?s=20)?)"
    re_tiktok = r"https?://(?:www\.)?tiktok\.com/(?:@[a-zA-Z0-9_.]+|[a-zA-Z0-9_]+)/(?:[a-zA-Z0-9_]+|video/\d+)(?:\S+)?"
    re_instagram = r"https?://www\.instagram\.com/\S+"

    @staticmethod
    def detect_link(text: str) -> Tuple[Optional[LinkType], Optional[str]]:
        has_link = re.search(MediaLinkFormatter.re_link, text)
        if not has_link:
            return None, None

        if twitter_match := re.search(MediaLinkFormatter.re_twitter, text):
            return LinkType.TWITTER, twitter_match.group(1)

        if tiktok_match := re.search(MediaLinkFormatter.re_tiktok, text):
            return LinkType.TIKTOK, tiktok_match.group(0)

        if intagram_match := re.search(MediaLinkFormatter.re_instagram, text):
            return LinkType.INSTAGRAM, intagram_match.group(0)

        return None, None

    @staticmethod
    def embed_twitter(twitter_link: str) -> str:
        return re.sub(
            r"https?://(?:www\.)?(?:twitter\.com|x\.com)",
            "https://fxtwitter.com",
            twitter_link,
        )

    @staticmethod
    def embed_tiktok(tiktok_link: str) -> str:
        data = {"input_text": tiktok_link, "detailed": False}
        response = requests.post(
            "https://api.quickvids.win/v1/shorturl/create", json=data
        ).json()

        return response["quickvids_url"]

    @staticmethod
    def embed_instagram(instagram_link: str) -> str:
        return re.sub(
            r"www\.instagram",
            "www.ddinstagram",
            instagram_link,
        )
