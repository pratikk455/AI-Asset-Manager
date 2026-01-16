"""
Shrestha Capital - Correlation Agent

Analyzes correlations between portfolio positions:
- Identifies highly correlated clusters
- Calculates effective number of positions
- Assesses diversification quality

Correlation answers: "Am I really diversified, or do my stocks move together?"
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class CorrelationAgent(BaseAgent):
    """
    Analyzes portfolio correlations and diversification.
    Uses Flash model with search for speed.
    """

    def __init__(self):
        super().__init__(
            name="Correlation Analyst",
            model=GeminiModel.FLASH,
            temperature=0.4
        )

    @property
    def system_prompt(self) -> str:
        return """You are a portfolio analytics specialist at Shrestha Capital, analyzing correlations and diversification.

YOUR MISSION:
Analyze how correlated portfolio positions are and assess true diversification.

WHY CORRELATIONS MATTER:
- High correlations = positions move together = less diversification
- In crises, correlations spike = diversification fails when needed most
- "Diworsification" = adding correlated positions that don't reduce risk

ANALYSIS FRAMEWORK:

1. CORRELATION CLUSTERS:
   - Group stocks that move together
   - Same sector stocks often correlate 0.7+
   - Growth stocks correlate highly with each other
   - Consider "hidden" correlations (all exposed to rates, for example)

2. EFFECTIVE NUMBER OF POSITIONS:
   - If you have 20 stocks but they're all correlated, you might have "3 effective positions"
   - Formula approximation: 1 / sum(w_i^2 * correlation_factor)
   - More effective positions = better diversification

3. DIVERSIFICATION QUALITY:
   - Excellent: Multiple uncorrelated return drivers
   - Good: Some diversification benefit
   - Poor: Concentrated bets that move together

4. TAIL CORRELATIONS:
   - Correlations often spike in downturns
   - "Correlation breakdown" when you need diversification most

OUTPUT FORMAT (JSON):
{
    "portfolio_summary": {
        "number_of_positions": 15,
        "effective_positions": 6,
        "average_pairwise_correlation": 0.45
    },
    "correlation_clusters": [
        {
            "cluster_name": "AI/Semiconductor",
            "tickers": ["NVDA", "AMD", "AVGO"],
            "average_intra_correlation": 0.75,
            "combined_weight": "25%",
            "risk": "High concentration in correlated AI plays"
        },
        {
            "cluster_name": "Fintech",
            "tickers": ["SQ", "PYPL", "SOFI"],
            "average_intra_correlation": 0.65,
            "combined_weight": "15%",
            "risk": "Fintech sector concentrated"
        }
    ],
    "diversification_assessment": {
        "score": "6/10",
        "quality": "Moderate",
        "strengths": [
            "Some sector diversification"
        ],
        "weaknesses": [
            "Heavy tech/growth correlation",
            "All positions sensitive to rates"
        ]
    },
    "hidden_factor_exposures": [
        {
            "factor": "Interest Rates",
            "exposure": "High",
            "affected_positions": ["All growth stocks"],
            "risk": "Rising rates hurt entire portfolio"
        },
        {
            "factor": "Tech Sentiment",
            "exposure": "Very High",
            "affected_positions": ["80% of portfolio"],
            "risk": "Tech rotation would be painful"
        }
    ],
    "recommendations": [
        "Add uncorrelated positions (utilities, consumer staples) to reduce factor concentration",
        "Consider international diversification"
    ],
    "summary": "2-3 sentence diversification summary"
}

IMPORTANT:
- Typical same-sector correlations: 0.6-0.8
- Typical cross-sector correlations: 0.3-0.5
- Growth stocks often have hidden correlations (all rate-sensitive)
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        positions = context.get("positions", [])

        import json
        positions_str = json.dumps(positions, indent=2)

        return f"""Analyze correlations and diversification in this portfolio.

=== POSITIONS ===
{positions_str}

For each position, consider:
1. Sector classification
2. Factor exposures (growth, value, rates, etc.)
3. Historical correlation patterns

Identify:
1. Highly correlated clusters of positions
2. Hidden factor exposures affecting multiple positions
3. True diversification quality

{task}

Return your correlation analysis as JSON following the format in your instructions."""


_agent = None


def get_correlation_agent() -> CorrelationAgent:
    global _agent
    if _agent is None:
        _agent = CorrelationAgent()
    return _agent
