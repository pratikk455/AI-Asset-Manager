"""
Transaction model - records buy/sell actions
"""

from sqlalchemy import String, Text, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from decimal import Decimal

from .base import Base, generate_uuid


class Transaction(Base):
    """
    Records a buy/sell transaction in a fund.
    """

    __tablename__ = "transactions"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)

    # Foreign key to fund
    fund_id: Mapped[str] = mapped_column(String(36), ForeignKey("funds.id", ondelete="CASCADE"))

    # Transaction details
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # buy, sell, trim, add
    shares: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    total_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # Reason/notes
    reason: Mapped[Optional[str]] = mapped_column(Text)

    # Who approved
    approved_by: Mapped[Optional[str]] = mapped_column(String(20))  # user, agent, system

    # Timestamp
    executed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    fund: Mapped["Fund"] = relationship("Fund", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction({self.action} {self.ticker})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fund_id": self.fund_id,
            "ticker": self.ticker,
            "action": self.action,
            "shares": float(self.shares) if self.shares else None,
            "price": float(self.price) if self.price else None,
            "total_value": float(self.total_value) if self.total_value else None,
            "reason": self.reason,
            "approved_by": self.approved_by,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }
