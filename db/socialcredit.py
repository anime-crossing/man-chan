from typing import List, Optional

from sqlalchemy import Integer
from sqlalchemy.orm import column_property
from sqlalchemy.schema import Column

from .base import Base


class UserCredit(Base):
    __tablename__ = "usercredit"

    positives = Column(Integer, default=0)
    negatives = Column(Integer, default=0)
    current_score = column_property(positives - negatives)

    @classmethod
    def create(cls, discord_id: str) -> "UserCredit":
        new_user = cls._create(id=discord_id)
        return new_user

    @classmethod
    def get(cls, discord_id: str) -> Optional["UserCredit"]:
        return cls._query().filter_by(id=discord_id).first()

    @classmethod
    def leaderboard(cls) -> List["UserCredit"]:
        return cls._query().order_by(UserCredit.current_score.desc()).all()

    def increase_score(self, change: int):
        self.positives += change
        self._save()

    def decrease_score(self, change: int):
        self.negatives += change
        self._save()
