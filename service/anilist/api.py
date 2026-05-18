import datetime
import logging
import operator
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import requests
from disnake import ButtonStyle, Color, Embed, Interaction
from disnake.ext import commands
from disnake.ui import Button, Modal, Select, TextInput, View

from db.anilist_users import AnilistUsers
from main import ManChanBot
from models.anilist_queries import AnilistQueries
from service.anilist.interaction import AnilistInteraction
from utils.context import get_member
from utils.distyping import Context


class AnilistStatus(Enum):
    ERROR = 0
    SUCCESS = 1
    NOT_FOUND = 2


ResponseType = Tuple[AnilistStatus, Optional[Dict[str, Any]]]


class AnilistAPI:
    ANILIST_URL = "https://graphql.anilist.co"

    @classmethod
    def query_profile(cls, anilist_name: str) -> ResponseType:
        query = AnilistQueries.account
        variables = {"name": anilist_name}

        result = cls._send_post(query=query, variables=variables)

        if result.status_code != 200:
            return AnilistStatus.ERROR, None

        parsed = result.json()
        if "errors" in parsed:
            return AnilistStatus.NOT_FOUND, None

        return AnilistStatus.SUCCESS, parsed

    @staticmethod
    def _send_post(query: str, variables: Dict[str, Any]) -> requests.Response:
        return requests.post(
            url=AnilistAPI.ANILIST_URL, json={"query": query, "variables": variables}
        )
