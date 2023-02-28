from typing import Optional

from sqlalchemy import Integer, Float, String, Boolean
from sqlalchemy.schema import Column

from .base import Base

class Invoice_Participant(Base):
    __tablename__ = "invoice_participants"
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(String, default = None)
    participant_id = Column(Integer, default = None)
    amount_owed = Column(Float, default= 0.00)
    paid = Column(Boolean, default=False)

    @classmethod
    def create(cls, invoice: str, pid: int, cost: float, status: bool) -> "Invoice_Participant":
        new_record = cls._create(invoice_id=invoice, participant_id=pid, amount_owed=cost, paid=status)
        return new_record

    @classmethod
    def get(cls, pid: int, iid: str) -> Optional["Invoice_Participant"]:
        return cls._query().filter_by(participant_id=pid, invoice_id=iid).first()
    
    @classmethod
    def get_latest(cls, pid: int) -> Optional["Invoice_Participant"]:
        return cls._query().filter_by(participant_id=pid).order_by(cls.id.desc()).first()