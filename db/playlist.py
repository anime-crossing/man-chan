from typing import List, Optional

from sqlalchemy import Integer, String
from sqlalchemy.schema import Column

from .base import Base


class PlaylistDB(Base):
    __tablename__ = "playlist"

    discord_id = Column(Integer, nullable=False)
    playlist_name = Column(String, default="", unique=True, nullable=False)

    @classmethod
    def create(cls, discord_id: int, name: str) -> None:
        cls._create(discord_id=discord_id, playlist_name=name)

    @classmethod
    def get(cls, id: int, discord_id: int) -> Optional["PlaylistDB"]:
        return cls._query().filter_by(discord_id=discord_id, id=id).first()

    @classmethod
    def get_by_id(cls, id: int) -> Optional["PlaylistDB"]:
        return cls._query().filter_by(id=id).first()

    @classmethod
    def get_all(cls) -> List["PlaylistDB"]:
        return cls._query().all()

    @classmethod
    def delete(cls, id: int):
        cls._delete(id=id)
