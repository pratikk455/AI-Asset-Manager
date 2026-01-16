"""
Shrestha Capital - Attribution Agent

Explains what drove fund returns:
- Stock selection effect (picking winners/losers)
- Sector allocation effect (over/underweight sectors)
- Timing effect (when you bought/sold)

Answers: "Why did we outperform/underperform?"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class AttributionAgent(BaseAgent):
    """
    Attributes fund returns to various factors.
    Uses Pro model for sophisticated analysis.
    """

    def __init__(self):
        super().__init__(
            name="Attribution Analyst",
            model=GeminiModel.PRO,
            temperature=0.4
        )

    @property
    def system_prompt(self) -> str:
        return """You are a performance attribution analyst at Shrestha Capital.

YOUR MISSION:
Explain what drove fund returns by decomposing performance into components.

ATTRIBUTION FRAMEWORK:

1. STOCK SELECTION EFFECT:
   - Did we pick good stocks within sectors?
   - Winners: Stocks that beat their sector
   - Losers: Stocks that lagged their sector

2. SECTOR ALLOCATION EFFECT:
   - Did we overweight winning sectors?
   - Did we underweight losing sectors?

3. INTERACTION EFFECT:
   - Combined effect of selection + allocation

4. POSITION-LEVEL CONTRIBUTION:
   - Each position's contribution to total return
   - Contribution = Weight × Return

TOP/BOTTOM CONTRIBUTORS:
- Identify the 5 biggest contributors (helped returns)
- Identify the 5 biggest detractors (hurt returns)

OUTPUT FORMAT (JSON):
{
    "attribution_period": "YTD 2024",
    "fund_return": "+15.5%",
    "benchmark_return": "+12.0%",
    "alpha": "+3.5%",
    "attribution_breakdown": {
        "stock_selection": "+2.5%",
        "sector_allocation": "+0.8%",
        "interaction": "+0.2%",
        "total_alpha": "+3.5%"
    },
    "top_contributors": [
        {
            "ticker": "NVDA",
            "weight": "8%",
            "return": "+80%",
            "contribution": "+6.4%",
            "why": "AI demand drove massive outperformance"
        }
    ],
    "top_detractors": [
        {
            "ticker": "PYPL",
            "weight": "4%",
            "return": "-20%",
            "contribution": "-0.8%",
            "why": "Competition pressures hurt margins"
        }
    ],
    "sector_attribution": [
        {
            "sector": "Technology",
            "portfolio_weight": "45%",
            "benchmark_weight": "30%",
            "sector_return": "+25%",
            "allocation_effect": "+1.5%"
        }
    ],
    "key_insights": [
        "Stock selection in tech drove most of alpha",
        "Underweight in energy helped in Q1"
    ],
    "lessons_learned": [
        "High conviction positions generated outsized returns"
    ],
    "summary": "2-3 sentence attribution summary"
}

IMPORTANT:
- Be precise about what drove returns
- Distinguish between skill and luck
- Contributions should roughly sum to total return
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True  # Need position returns

    def _build_prompt(self, task: str, context: dict) -> str:
        positions = context.get("positions", [])
        fund_return = context.get("fund_return", 0)
        benchmark = context.get("benchmark", "SPY")

        import json
        positions_str = json.dumps(positions, indent=2) if positions else "No positions"

        return f"""Perform return attribution analysis.

=== FUND PERFORMANCE ===
Fund Return: {fund_return:.1%}
Benchmark: {benchmark}

=== POSITIONS ===
{positions_str}

Search for:
1. Return of each position over the period
2. Benchmark return
3. Sector returns for context

Decompose the fund's returns into:
1. Stock selection effect
2. Sector allocation effect
3. Top contributors and detractors

{task}

Return your attribution analysis as JSON following the format in your instructions."""


_agent = None


def get_attribution_agent() -> AttributionAgent:
    global _agent
    if _agent is None:
        _agent = AttributionAgent()
    return _agent
