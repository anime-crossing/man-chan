from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.schema import Column

from models import Song

from .base import Base


class SongDB(Base):
    __tablename__ = "song"

    title = Column(String, default="", nullable=False)
    url = Column(String, default="", nullable=False)
    thumbnail_url = Column(String, default="")
    webpage_url = Column(String, unique=True, default="")

    @classmethod
    def create(cls, song: Song) -> "SongDB":
        title = song.title
        url = song.url
        thumbnail_url = song.thumbnail_url
        webpage_url = song.webpage_url
        new_song = cls._create(
            title=title, url=url, thumbnail_url=thumbnail_url, webpage_url=webpage_url
        )
        return new_song

    @classmethod
    def get_by_id(cls, id: int) -> Optional["SongDB"]:
        return cls._query().filter_by(id=id).first()

    @classmethod
    def get_by_url(cls, song_url: str) -> Optional["SongDB"]:
        return cls._query().filter_by(url=song_url).first()

    @classmethod
    def get_all(cls, url: str) -> Optional[List[Song]]:
        return cls._query().all()
