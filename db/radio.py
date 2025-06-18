from typing import Optional

from sqlalchemy import Integer
from sqlalchemy.schema import Column

from .base import Base


class RadioDB(Base):
    __tablename__ = "radio"

    guild_id = Column(Integer, nullable=False)
    channel_id = Column(Integer, nullable=False)
    embed_id = Column(Integer, nullable=False)

    @classmethod
    def create(cls, guild_id: str, channel_id: str, embed_id: str) -> None:
        cls._create(guild_id=guild_id, channel_id=channel_id, embed_id=embed_id)

    @classmethod
    def get(cls, guild_id: str) -> Optional["RadioDB"]:
        return cls._query().filter_by(guild_id=guild_id).first()

    @classmethod
    def delete(cls, guild_id: str):
        cls._delete(guild_id=guild_id)
