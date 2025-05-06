from typing import List

from sqlalchemy import Integer
from sqlalchemy.schema import Column

from .base import Base


class PlaylistSongDB(Base):
    __tablename__ = "playlistSong"

    playlist_id = Column(Integer, nullable=False)
    song_id = Column(Integer, nullable=False)

    # __table_args__ = (
    #     UniqueConstraint("playlist_id", "song_id", name="unique_playlist_song"),
    # )

    @classmethod
    def create(cls, playlist_id: int, song_id: int) -> None:
        cls._create(playlist_id=playlist_id, song_id=song_id)

    @classmethod
    def get_songs_by_playlist(cls, playlist_id: int) -> List["PlaylistSongDB"]:
        return cls._query().filter_by(playlist_id=playlist_id).all()

    @classmethod
    def delete_playlist_song(cls, playlist_id: int, song_id: int) -> None:
        cls._delete(playlist_id=playlist_id, song_id=song_id)
