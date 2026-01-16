"""
Portfolio endpoints - portfolio construction and management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.portfolio.pm_agent import get_pm_agent
from agents.portfolio.rebalancing_agent import get_rebalancing_agent

router = APIRouter()


class ThesisInput(BaseModel):
    """Thesis input for portfolio construction"""
    ticker: str
    recommendation: str
    conviction: float
    thesis_summary: Optional[str] = None


class ConstructPortfolioRequest(BaseModel):
    """Request to construct a portfolio"""
    theses: List[ThesisInput]
    mandate: Optional[str] = None
    constraints: Optional[Dict] = None
    current_positions: Optional[List[Dict]] = None


class Position(BaseModel):
    """Position for rebalancing"""
    ticker: str
    target_weight: float
    current_weight: float


class RebalanceRequest(BaseModel):
    """Request for rebalancing analysis"""
    positions: List[Position]
    drift_threshold: float = 0.25


@router.post("/portfolio/construct")
async def construct_portfolio(request: ConstructPortfolioRequest):
    """
    Construct a portfolio from investment theses.

    The PM agent will:
    - Size positions based on conviction
    - Ensure diversification
    - Respect constraints
    - Allocate cash appropriately
    """
    try:
        agent = get_pm_agent()

        # Convert theses to list of dicts
        theses = [
            {
                "ticker": t.ticker.upper(),
                "recommendation": t.recommendation,
                "conviction": t.conviction,
                "thesis_summary": t.thesis_summary or f"Investment thesis for {t.ticker}"
            }
            for t in request.theses
        ]

        result = await agent.run(
            task="Construct the optimal portfolio",
            context={
                "theses": theses,
                "mandate": request.mandate,
                "constraints": request.constraints or {},
                "current_positions": request.current_positions or []
            }
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio/rebalance")
async def check_rebalancing(request: RebalanceRequest):
    """
    Check if portfolio needs rebalancing.

    Compares current weights to target weights
    and recommends trades if drift exceeds threshold.
    """
    try:
        agent = get_rebalancing_agent()

        positions = [
            {
                "ticker": p.ticker.upper(),
                "target_weight": p.target_weight,
                "current_weight": p.current_weight
            }
            for p in request.positions
        ]

        result = await agent.run(
            task="Analyze drift and recommend rebalancing",
            context={
                "positions": positions,
                "drift_threshold": request.drift_threshold
            }
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
