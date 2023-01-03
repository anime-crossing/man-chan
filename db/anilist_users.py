from typing import Optional

from sqlalchemy import Integer
from sqlalchemy.schema import Column

from .base import Base

class AnilistUsers(Base):
    __tablename__ = "anilist_users"

    anilist_id = Column(Integer, default=0)

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

    def set_anilist_id(self, anilist_id: int):
        self.anilist_id = anilist_id
        self._save()