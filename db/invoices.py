from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.schema import Column

from .base import Base


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(String, primary_key=True)
    payer_id = Column(Integer, default=0)
    total_cost = Column(Float, default=0.00)
    desc = Column(String, default=None)
    has_multi = Column(Boolean, default=False)
    closed = Column(Boolean, default=False)
    open_date = Column(Integer)
    close_date = Column(Integer)

    @classmethod
    def create(cls, uuid: str) -> "Invoice":
        new_invoice = cls._create(id=uuid)
        return new_invoice

    @classmethod
    def get(cls, uuid: str) -> Optional["Invoice"]:
        return cls._query().filter_by(id=uuid).first()

    @classmethod
    def get_latest(cls, discord_id: int, status: bool) -> Optional["Invoice"]:
        return cls._query().filter_by(payer_id=discord_id, closed = status).order_by(cls.open_date.desc()).first()

    def set_values(self, pay_id: int, amount: float, arg: str, timestamp: int, multi: bool):
        self.payer_id = pay_id
        self.total_cost = amount
        self.desc = arg
        self.open_date = timestamp
        self.has_multi = multi
        self._save()
    
    def close_bill(self, timestamp: int):
        self.closed = True
        self.close_date = timestamp
        self._save()
