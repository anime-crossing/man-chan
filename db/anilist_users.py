from __future__ import annotations

from typing import TYPE_CHECKING, cast

from sqlalchemy import Integer
from sqlalchemy.schema import Column

from .base import Base

if TYPE_CHECKING:
    from typing import List, Optional


class AnilistUsers(Base):
    __tablename__ = "anilist_users"

    anilist_id = Column[int](Integer, default=None)
    minutes_watched = Column[int](Integer, default=0)
    chapters_read = Column[int](Integer, default=0)

    @classmethod
    def create(cls, discord_id: int, anilist_id: Optional[int] = None) -> AnilistUsers:
        new_user = cls._create(id=discord_id, anilist_id=anilist_id)
        return new_user

    @classmethod
    def get(cls, discord_id: int) -> Optional["AnilistUsers"]:
        return cls._query().filter_by(id=discord_id).first()

    @classmethod
    def get_anilist_id(cls, discord_id: int) -> Optional[int]:
        user = cls.get(discord_id)
        if user is None or user.anilist_id is None:
            return None

        return cast(int, user.anilist_id)

    @classmethod
    def get_all(cls) -> List["AnilistUsers"]:
        return cls._query().all()

    @classmethod
    def anime_leaderboard(cls) -> List["AnilistUsers"]:
        return cls._query().filter(AnilistUsers.anilist_id.is_not(None)).order_by(AnilistUsers.minutes_watched.desc()).all()  # type: ignore

    @classmethod
    def manga_leaderboard(cls) -> List["AnilistUsers"]:
        return cls._query().filter(AnilistUsers.anilist_id.is_not(None)).order_by(AnilistUsers.chapters_read.desc()).all()  # type: ignore

    def set_anilist_id(self, anilist_id: Optional[int]) -> AnilistUsers:
        self.anilist_id = None if anilist_id == 0 or anilist_id is None else anilist_id
        self._save()
        return self

    def update_stats(self, minutes: int, chapters: int):
        self.minutes_watched = minutes
        self.chapters_read = chapters
        self._save()
