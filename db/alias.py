from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.schema import Column

from .base import Base


class Aliases(Base):
    __tablename__ = "alias"

    alias = Column(String, default=None)

    @classmethod
    def create(cls, discord_id: int) -> "Aliases":
        new_user = cls._create(id=discord_id)
        return new_user

    @classmethod
    def get(cls, discord_id: int) -> Optional["Aliases"]:
        return cls._query().filter_by(id=discord_id).first()

    @classmethod
    def get_list(cls) -> List["Aliases"]:
        return cls._query().order_by(Aliases.alias.asc()).all()  # type: ignore

    def set_alias(self, alias: Optional[str]):
        self.alias = alias
        self._save()
