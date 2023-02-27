from typing import List, Optional

from sqlalchemy import Integer
from sqlalchemy.schema import Column

from .base import Base


class AnilistUsers(Base):
    __tablename__ = "anilist_users"

    anilist_id = Column(Integer, default=None)
    minutes_watched = Column(Integer, default=0)
    chapters_read = Column(Integer, default=0)

    @classmethod
    def create(cls, discord_id: int) -> "AnilistUsers":
        new_user = cls._create(id=discord_id)
        return new_user
    
    @classmethod
    def get(cls, discord_id: int) -> Optional["AnilistUsers"]:
        return cls._query().filter_by(id=discord_id).first()

    @classmethod
    def get_anilist_id(cls, discord_id: int) -> Optional[int]:
        user = cls.get(discord_id)
        if user:
            return user.anilist_id

    @classmethod
    def get_all(cls) -> List["AnilistUsers"]:
        return cls._query().all()

    @classmethod
    def anime_leaderboard(cls) -> List["AnilistUsers"]:
        return cls._query().filter(AnilistUsers.anilist_id.is_not(None)).order_by(AnilistUsers.minutes_watched.desc()).all()  # type: ignore

    @classmethod
    def manga_leaderboard(cls) -> List["AnilistUsers"]:
        return cls._query().filter(AnilistUsers.anilist_id.is_not(None)).order_by(AnilistUsers.chapters_read.desc()).all()  # type: ignore

    def set_anilist_id(self, anilist_id: int):
        self.anilist_id = anilist_id if anilist_id != 0 else None
        self._save()

    def update_stats(self, minutes: int, chapters: int):
        self.minutes_watched = minutes
        self.chapters_read = chapters
        self._save()
