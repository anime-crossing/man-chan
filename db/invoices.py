from typing import Optional

from sqlalchemy import Float, Integer, String
from sqlalchemy.schema import Column

from .base import Base


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(String, primary_key=True)
    payer_id = Column(Integer, default=0)
    total_cost = Column(Float, default=0.00)
    desc = Column(String, default=None)
    date = Column(Integer)

    @classmethod
    def create(cls, uuid: str) -> "Invoice":
        new_invoice = cls._create(id=uuid)
        return new_invoice

    @classmethod
    def get(cls, uuid: str) -> Optional["Invoice"]:
        return cls._query().filter_by(id=uuid).first()

    @classmethod
    def get_latest(cls) -> Optional["Invoice"]:
        return cls._query().order_by(cls.id.desc()).first()

    def set_values(self, pay_id: int, amount: float, arg: str, timestamp: int):
        self.payer_id = pay_id
        self.total_cost = amount
        self.desc = arg
        self.date = timestamp
        self._save()
