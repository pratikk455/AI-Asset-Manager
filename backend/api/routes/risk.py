"""
Risk endpoints - portfolio risk analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestrator.pipelines.risk_pipeline import RiskPipeline

router = APIRouter()


class Position(BaseModel):
    """Position for risk analysis"""
    ticker: str
    weight: float
    company: Optional[str] = None


class RiskAnalysisRequest(BaseModel):
    """Request for risk analysis"""
    positions: List[Position]
    portfolio_value: float = 1000000
    run_full: bool = True


@router.post("/risk/analyze")
async def analyze_risk(request: RiskAnalysisRequest):
    """
    Run comprehensive risk analysis on a portfolio.

    Analyzes:
    - Stress tests (2008, 2020, 2022 scenarios)
    - Value at Risk (VaR)
    - Monte Carlo simulations
    - Correlation/diversification

    Returns a complete risk report.
    """
    try:
        pipeline = RiskPipeline()

        # Convert positions to list of dicts
        positions = [
            {
                "ticker": p.ticker.upper(),
                "weight": p.weight,
                "company": p.company or p.ticker.upper()
            }
            for p in request.positions
        ]

        result = await pipeline.analyze(
            positions=positions,
            portfolio_value=request.portfolio_value,
            run_full=request.run_full
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk/stress-test")
async def stress_test(request: RiskAnalysisRequest):
    """
    Run only stress tests on a portfolio.
    Faster than full risk analysis.
    """
    try:
        from agents.risk.stress_test_agent import get_stress_test_agent

        agent = get_stress_test_agent()

        positions = [
            {"ticker": p.ticker.upper(), "weight": p.weight}
            for p in request.positions
        ]

        result = await agent.run(
            task="Run stress tests",
            context={"positions": positions, "portfolio_value": request.portfolio_value}
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk/var")
async def calculate_var(request: RiskAnalysisRequest):
    """
    Calculate Value at Risk for a portfolio.
    """
    try:
        from agents.risk.var_agent import get_var_agent

        agent = get_var_agent()

        positions = [
            {"ticker": p.ticker.upper(), "weight": p.weight}
            for p in request.positions
        ]

        result = await agent.run(
            task="Calculate VaR",
            context={"positions": positions, "portfolio_value": request.portfolio_value}
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
