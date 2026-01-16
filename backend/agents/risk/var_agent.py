"""
Shrestha Capital - Value at Risk (VaR) Agent

Calculates portfolio Value at Risk:
- Daily VaR at 95% and 99% confidence
- Weekly and monthly VaR
- Component VaR (contribution by position)

VaR answers: "What's the most I could lose on a bad day?"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class VaRAgent(BaseAgent):
    """
    Calculates Value at Risk for a portfolio.
    Uses Flash model - mostly calculation based.
    """

    def __init__(self):
        super().__init__(
            name="VaR Analyst",
            model=GeminiModel.FLASH,
            temperature=0.3
        )

    @property
    def system_prompt(self) -> str:
        return """You are a quantitative risk analyst at Shrestha Capital, calculating Value at Risk (VaR).

YOUR MISSION:
Calculate VaR metrics for a portfolio to quantify downside risk.

VALUE AT RISK EXPLAINED:
- VaR answers: "What's the maximum loss at X% confidence over Y period?"
- 95% Daily VaR of $10,000 means: "On 95% of days, losses won't exceed $10,000"
- The 5% worst days could be MUCH worse than VaR

VaR CALCULATIONS:

1. PARAMETRIC VaR (Variance-Covariance):
   - Assumes normal distribution
   - VaR = Portfolio Value × z-score × σ
   - 95% z-score = 1.645
   - 99% z-score = 2.326

2. HISTORICAL VaR:
   - Based on actual historical returns
   - 95% VaR = 5th percentile of historical returns
   - More realistic for fat-tailed distributions

3. COMPONENT VaR:
   - Each position's contribution to total VaR
   - Helps identify which positions add most risk

METRICS TO CALCULATE:
- Daily VaR (95% and 99%)
- Weekly VaR (daily × √5)
- Monthly VaR (daily × √21)
- Component VaR for each position

OUTPUT FORMAT (JSON):
{
    "portfolio_summary": {
        "total_value": "$1,000,000",
        "number_of_positions": 15,
        "portfolio_volatility_annual": "25%",
        "portfolio_volatility_daily": "1.58%"
    },
    "var_metrics": {
        "daily_var_95": {
            "amount": "$26,000",
            "percent": "2.6%",
            "interpretation": "On 95% of days, losses won't exceed $26,000"
        },
        "daily_var_99": {
            "amount": "$37,000",
            "percent": "3.7%",
            "interpretation": "On 99% of days, losses won't exceed $37,000"
        },
        "weekly_var_95": {
            "amount": "$58,000",
            "percent": "5.8%"
        },
        "monthly_var_95": {
            "amount": "$119,000",
            "percent": "11.9%"
        }
    },
    "component_var": [
        {
            "ticker": "NVDA",
            "weight": "10%",
            "volatility": "45%",
            "var_contribution": "25%",
            "marginal_var": "$6,500"
        }
    ],
    "risk_concentration": {
        "top_3_positions_var_contribution": "55%",
        "assessment": "Concentrated risk in top holdings"
    },
    "historical_context": {
        "worst_daily_loss_estimate": "-8%",
        "probability_of_10pct_monthly_loss": "5%"
    },
    "recommendations": [
        "Consider reducing NVDA position to lower VaR concentration"
    ],
    "summary": "2-3 sentence VaR summary"
}

IMPORTANT:
- Use realistic volatility estimates for each stock
- Growth stocks typically have 30-50% annual volatility
- Portfolio volatility is less than weighted average (diversification)
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True  # Need to look up volatility data

    def _build_prompt(self, task: str, context: dict) -> str:
        positions = context.get("positions", [])
        portfolio_value = context.get("portfolio_value", 1000000)

        import json
        positions_str = json.dumps(positions, indent=2)

        return f"""Calculate Value at Risk for this portfolio.

=== PORTFOLIO ===
Total Value: ${portfolio_value:,.0f}

=== POSITIONS ===
{positions_str}

Search for current volatility data for each position, then calculate:
1. Portfolio volatility (accounting for correlations/diversification)
2. Daily VaR at 95% and 99% confidence
3. Weekly and monthly VaR
4. Component VaR for each position

{task}

Return your VaR analysis as JSON following the format in your instructions."""


_agent = None


def get_var_agent() -> VaRAgent:
    global _agent
    if _agent is None:
        _agent = VaRAgent()
    return _agent
