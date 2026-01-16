"""
Position model - represents a holding in a fund
"""

from sqlalchemy import String, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from decimal import Decimal

from .base import Base, generate_uuid


class Position(Base):
    """
    A position (holding) in a fund.
    Tracks target weight, current weight, shares, cost basis, etc.
    """

    __tablename__ = "positions"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)

    # Foreign key to fund
    fund_id: Mapped[str] = mapped_column(String(36), ForeignKey("funds.id", ondelete="CASCADE"))

    # Stock info
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(255))

    # Weights (stored as decimals, e.g., 0.08 for 8%)
    target_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    current_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

    # Position details
    shares: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    cost_basis: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    current_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    market_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # P&L
    unrealized_pnl: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    unrealized_pnl_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))

    # Link to thesis
    thesis_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("theses.id"))

    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, watching, sold

    # Timestamps
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    fund: Mapped["Fund"] = relationship("Fund", back_populates="positions")
    thesis: Mapped[Optional["Thesis"]] = relationship("Thesis", back_populates="position")

    # Unique constraint
    __table_args__ = (
        # Unique ticker per fund
        {"sqlite_autoincrement": True},
    )

    def __repr__(self) -> str:
        return f"<Position(ticker='{self.ticker}', weight={self.target_weight})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fund_id": self.fund_id,
            "ticker": self.ticker,
            "company_name": self.company_name,
            "target_weight": float(self.target_weight) if self.target_weight else None,
            "current_weight": float(self.current_weight) if self.current_weight else None,
            "shares": float(self.shares) if self.shares else None,
            "cost_basis": float(self.cost_basis) if self.cost_basis else None,
            "current_price": float(self.current_price) if self.current_price else None,
            "market_value": float(self.market_value) if self.market_value else None,
            "unrealized_pnl": float(self.unrealized_pnl) if self.unrealized_pnl else None,
            "unrealized_pnl_pct": float(self.unrealized_pnl_pct) if self.unrealized_pnl_pct else None,
            "status": self.status,
        }
