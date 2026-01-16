"""
RiskReport model - periodic risk analysis
"""

from sqlalchemy import String, Date, Text, Numeric, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from .base import Base, generate_uuid


class RiskReport(Base):
    """
    Periodic risk report for a fund.
    Generated weekly by risk agents.
    """

    __tablename__ = "risk_reports"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)

    # Foreign key to fund
    fund_id: Mapped[str] = mapped_column(String(36), ForeignKey("funds.id", ondelete="CASCADE"))

    # Report date
    report_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Key metrics
    portfolio_beta: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 3))
    volatility_annual: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 4))
    sharpe_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 3))

    # Value at Risk
    var_daily_95: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    var_daily_99: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))

    # Drawdown
    max_drawdown: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 4))
    current_drawdown: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 4))

    # Detailed analysis (JSON)
    stress_tests: Mapped[Optional[dict]] = mapped_column(JSON)
    monte_carlo: Mapped[Optional[dict]] = mapped_column(JSON)
    correlations: Mapped[Optional[dict]] = mapped_column(JSON)
    factor_exposures: Mapped[Optional[dict]] = mapped_column(JSON)
    concentration: Mapped[Optional[dict]] = mapped_column(JSON)

    # Flags and recommendations
    flags: Mapped[Optional[dict]] = mapped_column(JSON)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSON)  # List of recommendations
    full_report: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    fund: Mapped["Fund"] = relationship("Fund", back_populates="risk_reports")

    def __repr__(self) -> str:
        return f"<RiskReport(date={self.report_date}, sharpe={self.sharpe_ratio})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fund_id": self.fund_id,
            "report_date": self.report_date.isoformat() if self.report_date else None,
            "metrics": {
                "portfolio_beta": float(self.portfolio_beta) if self.portfolio_beta else None,
                "volatility_annual": float(self.volatility_annual) if self.volatility_annual else None,
                "sharpe_ratio": float(self.sharpe_ratio) if self.sharpe_ratio else None,
                "var_daily_95": float(self.var_daily_95) if self.var_daily_95 else None,
                "var_daily_99": float(self.var_daily_99) if self.var_daily_99 else None,
                "max_drawdown": float(self.max_drawdown) if self.max_drawdown else None,
                "current_drawdown": float(self.current_drawdown) if self.current_drawdown else None,
            },
            "stress_tests": self.stress_tests,
            "monte_carlo": self.monte_carlo,
            "flags": self.flags,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
