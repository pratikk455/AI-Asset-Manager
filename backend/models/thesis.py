"""
Thesis model - investment thesis for a stock
"""

from sqlalchemy import String, Text, Numeric, ForeignKey, DateTime, JSON, ARRAY, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from .base import Base, generate_uuid


class Thesis(Base):
    """
    Investment thesis for a stock.
    Contains analysis from all agents + synthesized recommendation.
    """

    __tablename__ = "theses"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)

    # Foreign key to fund
    fund_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("funds.id"))

    # Stock info
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)

    # Recommendation
    recommendation: Mapped[Optional[str]] = mapped_column(String(20))  # strong_buy, buy, hold, sell, strong_sell
    conviction: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))  # 0.00 to 1.00
    target_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    target_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

    # Agent outputs (stored as JSON)
    fundamentals: Mapped[Optional[dict]] = mapped_column(JSON)
    moat_analysis: Mapped[Optional[dict]] = mapped_column(JSON)
    sentiment: Mapped[Optional[dict]] = mapped_column(JSON)
    valuation: Mapped[Optional[dict]] = mapped_column(JSON)

    # Synthesized thesis
    bull_case: Mapped[Optional[str]] = mapped_column(Text)
    bear_case: Mapped[Optional[str]] = mapped_column(Text)
    key_risks: Mapped[Optional[dict]] = mapped_column(JSON)  # List of risks
    catalysts: Mapped[Optional[dict]] = mapped_column(JSON)  # List of catalysts
    full_thesis: Mapped[Optional[str]] = mapped_column(Text)
    thesis_summary: Mapped[Optional[str]] = mapped_column(Text)

    # Score breakdown
    score_fundamentals: Mapped[Optional[int]] = mapped_column()
    score_moat: Mapped[Optional[int]] = mapped_column()
    score_sentiment: Mapped[Optional[int]] = mapped_column()
    score_valuation: Mapped[Optional[int]] = mapped_column()
    score_overall: Mapped[Optional[int]] = mapped_column()

    # Sources from web search
    sources: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    fund: Mapped[Optional["Fund"]] = relationship("Fund", back_populates="theses")
    position: Mapped[Optional["Position"]] = relationship("Position", back_populates="thesis", uselist=False)

    def __repr__(self) -> str:
        return f"<Thesis(ticker='{self.ticker}', recommendation='{self.recommendation}')>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fund_id": self.fund_id,
            "ticker": self.ticker,
            "recommendation": self.recommendation,
            "conviction": float(self.conviction) if self.conviction else None,
            "target_price": float(self.target_price) if self.target_price else None,
            "target_weight": float(self.target_weight) if self.target_weight else None,
            "bull_case": self.bull_case,
            "bear_case": self.bear_case,
            "key_risks": self.key_risks,
            "catalysts": self.catalysts,
            "thesis_summary": self.thesis_summary,
            "scores": {
                "fundamentals": self.score_fundamentals,
                "moat": self.score_moat,
                "sentiment": self.score_sentiment,
                "valuation": self.score_valuation,
                "overall": self.score_overall,
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_analysis(cls, ticker: str, analysis_result: dict, fund_id: str = None) -> "Thesis":
        """Create a Thesis from analysis pipeline output"""
        thesis_data = analysis_result.get("thesis", {})
        research = analysis_result.get("research", {})

        scores = thesis_data.get("score_breakdown", {})
        bull = thesis_data.get("bull_case", {})
        bear = thesis_data.get("bear_case", {})

        return cls(
            fund_id=fund_id,
            ticker=ticker,
            recommendation=thesis_data.get("recommendation"),
            conviction=thesis_data.get("conviction"),
            target_price=cls._parse_price(thesis_data.get("price_target")),
            target_weight=thesis_data.get("target_weight"),
            fundamentals=research.get("fundamentals"),
            moat_analysis=research.get("moat"),
            sentiment=research.get("sentiment"),
            valuation=research.get("valuation"),
            bull_case=bull.get("summary") if isinstance(bull, dict) else str(bull),
            bear_case=bear.get("summary") if isinstance(bear, dict) else str(bear),
            key_risks=thesis_data.get("key_risks"),
            catalysts=thesis_data.get("catalysts"),
            full_thesis=thesis_data.get("full_thesis"),
            thesis_summary=thesis_data.get("thesis_summary"),
            score_fundamentals=scores.get("fundamentals"),
            score_moat=scores.get("moat"),
            score_sentiment=scores.get("sentiment"),
            score_valuation=scores.get("valuation"),
            score_overall=scores.get("overall"),
            sources=analysis_result.get("sources"),
        )

    @staticmethod
    def _parse_price(price_str) -> Optional[Decimal]:
        """Parse price string like '$290' to Decimal"""
        if not price_str:
            return None
        try:
            clean = str(price_str).replace("$", "").replace(",", "").strip()
            return Decimal(clean)
        except:
            return None
