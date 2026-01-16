"""
Fund model - represents an investment fund
"""

from sqlalchemy import String, Text, Date, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from typing import Optional, List
import uuid

from .base import Base, generate_uuid


class Fund(Base):
    """
    Investment fund created and managed by the user.

    Examples:
    - "Shrestha Growth Fund" - US Large Cap Growth
    - "Fintech Disruptors" - Sector-specific fund
    """

    __tablename__ = "funds"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    mandate: Mapped[Optional[str]] = mapped_column(Text)  # Investment mandate/strategy
    category: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "US Large Cap Growth"

    # Benchmarks
    benchmark_primary: Mapped[Optional[str]] = mapped_column(String(20))  # e.g., "QQQ"
    benchmark_secondary: Mapped[Optional[str]] = mapped_column(String(20))  # e.g., "SPY"
    peer_funds: Mapped[Optional[dict]] = mapped_column(JSON)  # ["ARKK", "FDGRX", ...]

    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, active, closed

    # Configuration (constraints, risk limits, etc.)
    config: Mapped[Optional[dict]] = mapped_column(JSON)

    # Dates
    inception_date: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    positions: Mapped[List["Position"]] = relationship("Position", back_populates="fund", cascade="all, delete-orphan")
    theses: Mapped[List["Thesis"]] = relationship("Thesis", back_populates="fund", cascade="all, delete-orphan")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="fund", cascade="all, delete-orphan")
    snapshots: Mapped[List["DailySnapshot"]] = relationship("DailySnapshot", back_populates="fund", cascade="all, delete-orphan")
    risk_reports: Mapped[List["RiskReport"]] = relationship("RiskReport", back_populates="fund", cascade="all, delete-orphan")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="fund", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="fund", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Fund(name='{self.name}', status='{self.status}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "mandate": self.mandate,
            "category": self.category,
            "benchmark_primary": self.benchmark_primary,
            "benchmark_secondary": self.benchmark_secondary,
            "peer_funds": self.peer_funds,
            "status": self.status,
            "config": self.config,
            "inception_date": self.inception_date.isoformat() if self.inception_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
