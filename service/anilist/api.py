from enum import Enum
from typing import Any, Dict, Optional, Tuple

import requests

from models.anilist_queries import AnilistQueries


class AnilistStatus(Enum):
    ERROR = 0
    SUCCESS = 1
    NOT_FOUND = 2
    INTERNAL_ERROR = 3


class AnilistSearchOptions(Enum):
    ANIME = 0
    MANGA = 1
    NOVEL = 2


ResponseType = Tuple[AnilistStatus, Optional[Dict[str, Any]]]


class AnilistAPI:
    ANILIST_URL = "https://graphql.anilist.co"

    @classmethod
    def query_profile(cls, anilist_name: str) -> ResponseType:
        query = AnilistQueries.account
        variables = {"name": anilist_name}

        result = cls._send_post(query=query, variables=variables)
        parsed = result.json()
        if result.status_code == 404:
            return AnilistStatus.NOT_FOUND, None

        if result.status_code != 200:
            return AnilistStatus.ERROR, None

        return AnilistStatus.SUCCESS, parsed

    @classmethod
    def search_anime(
        cls, anime_name: str, media_type: AnilistSearchOptions
    ) -> ResponseType:
        query = AnilistQueries.search

        media_format = None
        subtype = None

        match media_type:
            case AnilistSearchOptions.ANIME:
                media_format = "ANIME"
            case AnilistSearchOptions.MANGA:
                media_format = "MANGA"
                subtype = "MANGA"
            case AnilistSearchOptions.NOVEL:
                media_format = "MANGA"
                subtype = "NOVEL"
            case _:
                pass

        if media_format is None:
            return AnilistStatus.INTERNAL_ERROR, None

        variables = {
            "type": media_format,
            "search": anime_name.strip(),
            "page": 1,
            "perPage": 10,
        }

        if subtype is not None:
            variables["format"] = subtype

        result = cls._send_post(query, variables)

        if result.status_code != 200:
            return AnilistStatus.ERROR, None

        parsed = result.json()
        if "errors" in parsed:
            return AnilistStatus.NOT_FOUND, None

        return AnilistStatus.SUCCESS, parsed

    @classmethod
    def get_anime_info(cls, media_id: str) -> ResponseType:
        query = AnilistQueries.media
        variables = {"id": media_id}

        result = cls._send_post(query, variables)
        if result.status_code != 200:
            return AnilistStatus.ERROR, None

        parsed = result.json()
        return AnilistStatus.SUCCESS, parsed

    @classmethod
    def get_score(cls, anilist_id: int, media_id: str) -> ResponseType:
        query = AnilistQueries.score
        variables = {"user": anilist_id, "id": media_id}

        result = cls._send_post(query, variables)
        if result.status_code != 200:
            return AnilistStatus.ERROR, None

        parsed = result.json()
        return AnilistStatus.SUCCESS, parsed

    @classmethod
    def get_user_info(cls, anilist_id: str) -> ResponseType:
        query = AnilistQueries.user_info
        variables = {"id": anilist_id}

        result = cls._send_post(query, variables)
        if result.status_code == 404:
            return AnilistStatus.NOT_FOUND, None

        if result.status_code != 200:
            return AnilistStatus.ERROR, None

        parsed = result.json()
        return AnilistStatus.SUCCESS, parsed

    @staticmethod
    def _send_post(query: str, variables: Dict[str, Any]) -> requests.Response:
        return requests.post(
            url=AnilistAPI.ANILIST_URL, json={"query": query, "variables": variables}
        )
