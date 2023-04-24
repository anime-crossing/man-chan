from datetime import datetime
from typing import Any, Dict, List, NamedTuple, Optional

import requests

from models.anilist_queries import AnilistQueries


class AnilistApi:
    api_url = "https://graphql.anilist.co"

    @classmethod
    def fetch_search_results(
        cls, media_type: str, query: str, format: Optional[str] = None
    ):
        variables = {"type": media_type, "search": query, "page": 1, "perPage": 10}
        if format is not None:
            variables["format"] = format

        json_response: Dict[str, Dict] = requests.post(
            AnilistApi.api_url,
            json={"query": AnilistQueries.search, "variables": variables},
        ).json()

        return _ResultFactory.page_result(json_response["data"]["Page"])

    @classmethod
    def fetch_media_info(cls, media_id: str):
        variables = {"id": media_id}
        json_response = requests.post(
            AnilistApi.api_url,
            json={"query": AnilistQueries.media, "variables": variables},
        ).json()

        return _ResultFactory.media_result(json_response["data"]["Media"])

    @classmethod
    def fetch_user_media_score(cls, media_id: str, anilist_id: int):
        variables = {"user": anilist_id, "id": media_id}
        json_response = requests.post(
            AnilistApi.api_url,
            json={"query": AnilistQueries.score, "variables": variables},
        ).json()

        if "errors" not in json_response:
            return _ResultFactory.media_user_info(json_response["data"]["MediaList"])


class _ResultFactory:
    @classmethod
    def page_result(cls, data: Dict[str, Any]) -> "_SearchResult":
        """Api result structural model when doing search"""
        per_page = data["pageInfo"]["perPage"]
        search_results = [cls.media_result(media) for media in data.get("media", [])]
        return _SearchResult(per_page=per_page, media=search_results)

    @classmethod
    def media_result(cls, data: Dict[str, Any]) -> "_MediaResult":
        """Api result structural model for a specific media"""
        return _MediaResult(
            id=data.get("id", 0),
            title=data.get("title", {}).get("romaji", ""),
            media_type=data.get("type", "UNKNOWN"),
            media_format=data.get("format", "UNKNOWN"),
            status=data.get("status", "UNKNOWN"),
            description=data.get("description", ""),
            episodes=data.get("episodes", "?"),
            image=data.get("coverImage", {}).get("extraLarge"),
            url=data.get("siteUrl"),
            avg_score=data.get("averageScore", "?"),
            genres=data.get("genres", []),
            start_date=cls.anilist_date(data.get("startDate", {})),
            end_date=cls.anilist_date(data.get("endDate", {})),
            chapters=data.get("chapters"),
            volumes=data.get("volumes"),
            studios=[
                studio.get("name", "")
                for studio in data.get("studios", {}).get("nodes", [])
            ],
            staff=cls.staff_list(data.get("staff", {})),
            popularity=data.get("popularity", 0),
        )

    @classmethod
    def media_user_info(cls, data: Dict[str, Any]) -> "_MediaUserScore":
        """Api result structural model for a specific user's statistics"""
        return _MediaUserScore(
            name=data.get("user", {}).get("name", ""),
            score=data.get("score", 0),
            status=data.get("status", ""),
            progress=data.get("progress", 0),
        )

    @classmethod
    def anilist_date(cls, date_entry: Dict[str, int]) -> "_AniDate":
        """Api result structural model for a date"""
        return _AniDate(
            year=date_entry.get("year"),
            month=date_entry.get("month"),
            day=date_entry.get("day"),
        )

    @classmethod
    def staff_list(
        cls, staff_json: Dict[str, List[Dict[str, Any]]]
    ) -> List["_StaffMember"]:
        """Api result structural model for a list of staff members"""
        result = []

        for edge, node in zip(staff_json.get("edges", []), staff_json.get("nodes", [])):
            result.append(
                _StaffMember(
                    role=edge.get("role", ""), name=node.get("name", {}).get("full", "")
                )
            )

        return result


# Response Models
class _SearchResult(NamedTuple):
    per_page: int
    media: List["_MediaResult"]


class _AniDate(NamedTuple):
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]

    def format_to_readable(self) -> str:
        if self.month is None:
            return str(self.year) if self.year else "?"

        month_name = datetime.strptime(str(self.month), "%m").strftime("%b")
        return f"{month_name}{f' {self.day},'  if self.day else ''} {self.year or ''}".strip(
            " ,"
        )


class _StaffMember(NamedTuple):
    role: str
    name: str


class _MediaResult(NamedTuple):
    id: int
    title: str
    media_type: str
    media_format: str
    status: str
    description: str
    episodes: str
    image: Optional[str]
    url: Optional[str]
    avg_score: int
    genres: List[str]
    start_date: _AniDate
    end_date: _AniDate
    chapters: Optional[int]
    volumes: Optional[int]
    studios: List[str]
    staff: List[_StaffMember]
    popularity: int

    def true_media_type(self) -> str:
        return self.media_type if self.media_format != "NOVEL" else "NOVEL"


class _MediaUserScore(NamedTuple):
    name: str
    score: int
    status: str
    progress: int
