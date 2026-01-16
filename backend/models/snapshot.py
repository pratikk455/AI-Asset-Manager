"""
DailySnapshot model - daily fund performance record
"""

from sqlalchemy import String, Date, Numeric, ForeignKey, DateTime, JSON, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from .base import Base, generate_uuid


class DailySnapshot(Base):
    """
    Daily snapshot of fund performance.
    Used for tracking returns over time.
    """

    __tablename__ = "daily_snapshots"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)

    # Foreign key to fund
    fund_id: Mapped[str] = mapped_column(String(36), ForeignKey("funds.id", ondelete="CASCADE"))

    # Date
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # Portfolio value
    total_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    cash: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # Returns
    daily_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 6))
    cumulative_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))

    # Benchmark comparison
    benchmark_daily_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 6))
    benchmark_cumulative_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    alpha_daily: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 6))

    # Snapshot of positions (JSON for flexibility)
    positions_snapshot: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    fund: Mapped["Fund"] = relationship("Fund", back_populates="snapshots")

    # Unique constraint: one snapshot per fund per day
    __table_args__ = (
        UniqueConstraint("fund_id", "date", name="uq_fund_date"),
    )

    def __repr__(self) -> str:
        return f"<DailySnapshot(date={self.date}, value={self.total_value})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fund_id": self.fund_id,
            "date": self.date.isoformat() if self.date else None,
            "total_value": float(self.total_value) if self.total_value else None,
            "cash": float(self.cash) if self.cash else None,
            "daily_return": float(self.daily_return) if self.daily_return else None,
            "cumulative_return": float(self.cumulative_return) if self.cumulative_return else None,
            "benchmark_daily_return": float(self.benchmark_daily_return) if self.benchmark_daily_return else None,
            "alpha_daily": float(self.alpha_daily) if self.alpha_daily else None,
        }
