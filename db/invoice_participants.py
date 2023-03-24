from typing import List, Optional, Tuple

from sqlalchemy import Boolean, Float, Integer, String, ForeignKey, func
from sqlalchemy.schema import Column

from .base import Base
from .invoices import Invoice


class Invoice_Participant(Base):
    __tablename__ = "invoice_participants"
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(String, ForeignKey('invoices.id'), default=None)
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
    def get_debt_all(cls, debt_id: int, param: int) -> List[Tuple[int, float]]:
        # param == 1 debt - param == 2 idk name yet
        if param == 1:
            result = cls._query([
                    Invoice.payer_id,
                    func.sum(cls.amount_owed)
                ])\
                .join(Invoice)\
                .filter(cls.participant_id == debt_id, cls.paid == False)\
                .group_by(Invoice.payer_id)\
                .all()
        else:
            result = cls._query([
                    cls.participant_id,
                    func.sum(cls.amount_owed)
                ])\
                .join(Invoice)\
                .filter(Invoice.payer_id == debt_id, cls.paid == False)\
                .group_by(cls.participant_id)\
                .all()

        return sorted([(row[0], float(row[1])) for row in result], key=lambda x: x[1], reverse=True)

    @classmethod
    def get_debt_specific(cls, debtor_id: int, debtee_id: int) -> float:

        value = cls._query([func.sum(cls.amount_owed)])\
            .join(Invoice)\
            .filter(cls.participant_id == debtor_id, Invoice.payer_id == debtee_id, cls.paid == False)\
            .scalar() or 0.0

        return float(value)

    
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
    
    def get_desc(self) -> str:
        bill = Invoice.get(self.invoice_id)

        return bill.desc if bill else '???'

    def set_paid(self, timestamp: int):
        self.paid = True
        self.paid_on = timestamp
        self._save()

    def set_unpaid(self):
        self.paid = False
        self.paid_on = None
        self._save()
