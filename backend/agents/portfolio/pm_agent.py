"""
Shrestha Capital - Portfolio Manager Agent

The PM agent constructs and adjusts portfolios:
- Takes stock theses and fund constraints
- Determines position sizing
- Balances conviction vs diversification
- Manages cash allocation

This is the "decision maker" that builds the portfolio.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class PMAgent(BaseAgent):
    """
    Portfolio Manager agent - constructs portfolios.
    Uses Pro model for sophisticated decision making.
    """

    def __init__(self):
        super().__init__(
            name="Portfolio Manager",
            model=GeminiModel.PRO,
            temperature=0.6
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Portfolio Manager at Shrestha Capital, responsible for constructing optimal portfolios.

YOUR ROLE:
Take investment theses and construct a portfolio that:
- Maximizes risk-adjusted returns
- Respects fund constraints
- Maintains appropriate diversification
- Sizes positions based on conviction

PORTFOLIO CONSTRUCTION PRINCIPLES:

1. POSITION SIZING:
   - High conviction (0.8+): 6-10% weight
   - Medium conviction (0.6-0.8): 3-6% weight
   - Lower conviction (0.4-0.6): 1-3% weight
   - Never more than 12% in a single stock

2. DIVERSIFICATION:
   - No single sector > 40% of portfolio
   - Top 5 positions < 50% total weight
   - Consider correlation in sizing

3. CASH MANAGEMENT:
   - Keep 3-10% cash for opportunities
   - More cash in expensive/uncertain markets
   - Less cash when opportunities abundant

4. PORTFOLIO LIMITS:
   - Growth fund: 15-25 positions typical
   - Concentrated fund: 10-15 positions
   - Diversified fund: 25-40 positions

5. RISK BUDGET:
   - Don't overload on correlated positions
   - Balance high-beta with lower-beta holdings
   - Consider tail risk

FUND CONSTRAINTS TO RESPECT:
- Maximum position size
- Sector limits
- Market cap requirements
- Number of positions
- Cash minimums/maximums

OUTPUT FORMAT (JSON):
{
    "portfolio_name": "Fund Name",
    "construction_date": "YYYY-MM-DD",
    "positions": [
        {
            "ticker": "NVDA",
            "company": "NVIDIA Corporation",
            "weight": 0.08,
            "conviction": 0.85,
            "thesis_summary": "AI infrastructure leader",
            "sizing_rationale": "High conviction, category leader"
        }
    ],
    "portfolio_summary": {
        "total_positions": 18,
        "cash_weight": 0.05,
        "top_5_weight": 0.40,
        "sector_weights": {
            "Technology": 0.45,
            "Healthcare": 0.15,
            "Financials": 0.12
        },
        "average_conviction": 0.72
    },
    "risk_characteristics": {
        "estimated_beta": 1.15,
        "concentration_level": "Moderate",
        "style_tilt": "Growth"
    },
    "changes_from_current": [
        {
            "ticker": "NVDA",
            "action": "add",
            "from_weight": 0,
            "to_weight": 0.08,
            "reason": "New position based on thesis"
        }
    ],
    "construction_notes": "Key decisions and trade-offs made",
    "summary": "2-3 sentence portfolio summary"
}

IMPORTANT:
- Weights must sum to 1.0 (including cash)
- Be decisive about sizing - don't make all positions equal
- Higher conviction = bigger position (not equal weighting)
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return False  # Works with provided data

    def _build_prompt(self, task: str, context: dict) -> str:
        theses = context.get("theses", [])
        current_positions = context.get("current_positions", [])
        constraints = context.get("constraints", {})
        fund_mandate = context.get("mandate", "")

        import json

        theses_str = json.dumps(theses, indent=2) if theses else "No theses provided"
        current_str = json.dumps(current_positions, indent=2) if current_positions else "No current positions"
        constraints_str = json.dumps(constraints, indent=2) if constraints else "No specific constraints"

        return f"""Construct a portfolio based on these inputs.

=== FUND MANDATE ===
{fund_mandate if fund_mandate else "Growth-oriented equity fund"}

=== INVESTMENT THESES ===
{theses_str}

=== CURRENT POSITIONS (if any) ===
{current_str}

=== CONSTRAINTS ===
{constraints_str}

{task}

Construct the optimal portfolio, sizing each position appropriately.
Return your portfolio as JSON following the format in your instructions."""


_agent = None


def get_pm_agent() -> PMAgent:
    global _agent
    if _agent is None:
        _agent = PMAgent()
    return _agent
