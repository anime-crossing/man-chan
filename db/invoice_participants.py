from typing import List, Optional

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.schema import Column

from .base import Base


class Invoice_Participant(Base):
    __tablename__ = "invoice_participants"
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(String, default=None)
    participant_id = Column(Integer, default=None)
    amount_owed = Column(Float, default=0.00)
    paid = Column(Boolean, default=False)
    paid_on = Column(Integer, default=None)

    @classmethod
    def create(cls, invoice: str, pid: int, cost: float) -> "Invoice_Participant":
        new_record = cls._create(
            invoice_id=invoice, participant_id=pid, amount_owed=cost
        )
        return new_record

    @classmethod
    def get(cls, pid: Optional[int], iid: str) -> Optional["Invoice_Participant"]:
        if pid is None:
            return cls._query().filter_by(invoice_id=iid).first()
        return cls._query().filter_by(participant_id=pid, invoice_id=iid).first()

    @classmethod
    def get_all(cls, pid: int) -> List["Invoice_Participant"]:
        return cls._query().filter_by(participant_id=pid).order_by(cls.id.desc()).all()

    @classmethod
    def get_participants(cls, bill_id: str, status: Optional[bool]) -> Optional[List["Invoice_Participant"]]:
        if status is None:
            return cls._query().filter_by(invoice_id=bill_id).all()    
        return cls._query().filter_by(invoice_id=bill_id, paid=status).all()

    @classmethod
    def get_latest(cls, pid: int, status: bool) -> Optional["Invoice_Participant"]:
        return (
            cls._query()
            .filter_by(participant_id=pid, paid=status)
            .order_by(cls.id.desc())
            .first()
        )

    def get_status(self, bill_id: str) -> bool:
        participants = self.get_participants(bill_id, None)

        if participants is not None:
            for participant in participants:
                if not participant.paid:
                    return False
        return True

    def set_paid(self, timestamp: int):
        self.paid = True
        self.paid_on = timestamp
        self._save()

    def set_unpaid(self):
        self.paid = False
        self.paid_on = None
        self._save()
