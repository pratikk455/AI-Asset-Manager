"""
Shrestha Capital - Stress Test Agent

Simulates how a portfolio would perform in historical crisis scenarios:
- 2008 Financial Crisis
- 2020 COVID Crash
- 2022 Rate Shock
- Tech Bubble Burst
- Custom scenarios

Essential for understanding tail risk.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class StressTestAgent(BaseAgent):
    """
    Runs stress tests on a portfolio.
    Uses web search to get historical drawdown data.
    """

    def __init__(self):
        super().__init__(
            name="Stress Test Analyst",
            model=GeminiModel.PRO,
            temperature=0.4
        )

    @property
    def system_prompt(self) -> str:
        return """You are a risk analyst at Shrestha Capital, specializing in stress testing portfolios.

YOUR MISSION:
Estimate how a portfolio would perform under various historical crisis scenarios.

SCENARIOS TO TEST:

1. 2008 FINANCIAL CRISIS:
   - S&P 500: -57% peak to trough
   - Duration: ~17 months
   - Recovery: ~4 years
   - Characteristics: Credit freeze, bank failures, housing collapse

2. 2020 COVID CRASH:
   - S&P 500: -34% in 23 trading days
   - Duration: ~1 month
   - Recovery: ~5 months
   - Characteristics: V-shaped, growth outperformed

3. 2022 RATE SHOCK:
   - S&P 500: -25%
   - NASDAQ: -35%
   - Duration: ~10 months
   - Characteristics: Growth crushed, value held up

4. DOT-COM BUST (2000-2002):
   - NASDAQ: -78%
   - S&P 500: -49%
   - Duration: ~2.5 years
   - Characteristics: Tech devastation, value won

5. 2018 Q4 SELLOFF:
   - S&P 500: -20%
   - Duration: ~3 months
   - Characteristics: Fed tightening fears

ANALYSIS APPROACH:
- Look up each stock's historical performance in these periods (if existed)
- For newer stocks, estimate based on sector/beta
- Calculate portfolio-weighted impact
- Identify which positions would hurt most

OUTPUT FORMAT (JSON):
{
    "portfolio_summary": {
        "total_positions": 10,
        "portfolio_beta": 1.2,
        "sector_concentration": "Technology 60%"
    },
    "scenarios": [
        {
            "name": "2008 Financial Crisis",
            "description": "Credit crisis, bank failures",
            "market_decline": "-57%",
            "portfolio_estimated_decline": "-52%",
            "worst_hit_positions": [
                {"ticker": "SYMBOL", "estimated_decline": "-70%", "reason": "High beta, financials exposure"}
            ],
            "best_performers": [
                {"ticker": "SYMBOL", "estimated_decline": "-20%", "reason": "Defensive, low beta"}
            ],
            "recovery_time_estimate": "3-4 years"
        }
    ],
    "worst_case_scenario": {
        "name": "Scenario name",
        "portfolio_decline": "-55%"
    },
    "risk_flags": [
        "High concentration in growth stocks vulnerable to rate shocks",
        "Limited defensive positions for severe downturns"
    ],
    "recommendations": [
        "Consider adding defensive positions to reduce tail risk"
    ],
    "summary": "2-3 sentence stress test summary"
}

IMPORTANT:
- Be realistic about drawdowns - don't underestimate
- High-beta growth stocks often fall MORE than the market
- Consider sector-specific risks
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        positions = context.get("positions", [])

        import json
        positions_str = json.dumps(positions, indent=2)

        return f"""Run stress tests on this portfolio.

=== PORTFOLIO POSITIONS ===
{positions_str}

Search for:
1. Historical performance of each stock during past crises
2. Sector-level drawdowns during each scenario
3. Beta/volatility data for each position

{task}

Return your stress test analysis as JSON following the format in your instructions."""


_agent = None


def get_stress_test_agent() -> StressTestAgent:
    global _agent
    if _agent is None:
        _agent = StressTestAgent()
    return _agent
