"""
Shrestha Capital - Monte Carlo Agent

Runs Monte Carlo simulations on portfolio returns:
- Simulates thousands of possible 1-year outcomes
- Provides probability distribution of returns
- Calculates probability of various outcomes

Monte Carlo answers: "What's the range of possible outcomes?"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class MonteCarloAgent(BaseAgent):
    """
    Runs Monte Carlo simulations on portfolio returns.
    Uses Pro model for sophisticated analysis.
    """

    def __init__(self):
        super().__init__(
            name="Monte Carlo Analyst",
            model=GeminiModel.PRO,
            temperature=0.4
        )

    @property
    def system_prompt(self) -> str:
        return """You are a quantitative analyst at Shrestha Capital, running Monte Carlo simulations.

YOUR MISSION:
Simulate the probability distribution of portfolio returns over 1 year using Monte Carlo methods.

MONTE CARLO APPROACH:

1. For each position:
   - Estimate expected annual return (based on growth, valuation, analyst targets)
   - Estimate annual volatility (historical or implied)

2. Simulate 10,000 paths:
   - Each path uses random returns drawn from distribution
   - Account for correlations between positions
   - Compound monthly or weekly returns

3. Analyze distribution:
   - Median outcome (50th percentile)
   - Upside scenarios (75th, 90th, 95th percentiles)
   - Downside scenarios (25th, 10th, 5th percentiles)
   - Probability of various outcomes

KEY ASSUMPTIONS:
- Use geometric Brownian motion for price paths
- Account for fat tails (markets aren't perfectly normal)
- Consider current market regime (growth vs value, volatility)

OUTPUT FORMAT (JSON):
{
    "simulation_params": {
        "num_simulations": 10000,
        "time_horizon": "1 year",
        "portfolio_expected_return": "15%",
        "portfolio_volatility": "28%"
    },
    "return_distribution": {
        "median_return": "12%",
        "mean_return": "14%",
        "percentile_5": "-25%",
        "percentile_10": "-15%",
        "percentile_25": "2%",
        "percentile_75": "28%",
        "percentile_90": "45%",
        "percentile_95": "55%"
    },
    "outcome_probabilities": {
        "prob_positive_return": "68%",
        "prob_beat_sp500": "55%",
        "prob_return_gt_20pct": "40%",
        "prob_loss_gt_10pct": "18%",
        "prob_loss_gt_20pct": "8%",
        "prob_loss_gt_30pct": "3%"
    },
    "best_case": {
        "scenario": "95th percentile",
        "return": "+55%",
        "drivers": "Strong AI demand, multiple expansion"
    },
    "worst_case": {
        "scenario": "5th percentile",
        "return": "-25%",
        "drivers": "Recession, multiple compression"
    },
    "position_contributions": [
        {
            "ticker": "NVDA",
            "weight": "10%",
            "expected_return": "25%",
            "volatility": "45%",
            "return_contribution": "2.5%"
        }
    ],
    "sensitivity_analysis": {
        "if_volatility_increases_50pct": "Downside risk increases significantly",
        "if_expected_returns_halved": "Probability of positive return drops to 52%"
    },
    "summary": "2-3 sentence Monte Carlo summary"
}

IMPORTANT:
- Be realistic about expected returns (don't be overly optimistic)
- High growth stocks often have high volatility
- Correlations increase in downturns (diversification fails when needed most)
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True  # Need volatility and expected return estimates

    def _build_prompt(self, task: str, context: dict) -> str:
        positions = context.get("positions", [])
        portfolio_value = context.get("portfolio_value", 1000000)

        import json
        positions_str = json.dumps(positions, indent=2)

        return f"""Run Monte Carlo simulation on this portfolio.

=== PORTFOLIO ===
Total Value: ${portfolio_value:,.0f}

=== POSITIONS ===
{positions_str}

For each position, search for:
1. Expected return estimates (analyst targets, growth rates)
2. Historical volatility
3. Correlation characteristics

Then run Monte Carlo analysis to project:
1. Distribution of 1-year returns
2. Probabilities of various outcomes
3. Best and worst case scenarios

{task}

Return your Monte Carlo analysis as JSON following the format in your instructions."""


_agent = None


def get_monte_carlo_agent() -> MonteCarloAgent:
    global _agent
    if _agent is None:
        _agent = MonteCarloAgent()
    return _agent
