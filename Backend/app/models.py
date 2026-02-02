#bacekend/app/model.py
from sqlalchemy import Column, String, Integer, Date, DateTime, UniqueConstraint
from datetime import datetime
from .database import Base
import uuid

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    amount_cents = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String)
    expense_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    idempotency_key = Column(String, nullable=True, unique=True)

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_idempotency_key"),
    )
