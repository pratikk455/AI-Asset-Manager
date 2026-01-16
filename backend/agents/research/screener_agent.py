"""
Shrestha Capital - Screener Agent

Takes raw scout output and categorizes stocks:
- HOT: High conviction, analyze immediately
- WARM: Interesting, analyze if capacity allows
- COLD: Pass for now, maybe revisit later

The screener is the gatekeeper before expensive analysis.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class ScreenerAgent(BaseAgent):
    """
    Screens scout output and categorizes stocks.
    Uses Flash model for speed - no search needed.
    """

    def __init__(self):
        super().__init__(
            name="Stock Screener",
            model=GeminiModel.FLASH,
            temperature=0.4  # Low temp for consistent categorization
        )

    @property
    def system_prompt(self) -> str:
        return """You are a stock screener at Shrestha Capital, deciding which stocks deserve deep analysis.

YOUR MISSION:
Review scout output and categorize each stock into HOT, WARM, or COLD based on:
- Quality of the growth thesis
- Market opportunity size
- Competitive position
- Valuation concerns
- Risk/reward profile

CATEGORIZATION CRITERIA:

HOT (Analyze Immediately):
- Clear, compelling growth thesis
- Large market opportunity
- Strong competitive position
- Reasonable valuation for growth
- Multiple scouts flagged it OR exceptionally strong signal
- Score: 8-10

WARM (Analyze If Capacity):
- Decent growth thesis but some questions
- Good but not exceptional opportunity
- Some competitive concerns
- Valuation may be stretched
- Single scout mention with moderate conviction
- Score: 5-7

COLD (Pass For Now):
- Weak or unclear thesis
- Limited market opportunity
- Significant competitive threats
- Expensive valuation without justification
- Speculative or hype-driven
- Score: 1-4

FUND-SPECIFIC FILTERS:
Consider the fund's mandate when screening:
- Growth fund → prioritize revenue growth
- Value fund → prioritize valuation
- Thematic fund → prioritize theme fit
- Quality fund → prioritize moat

OUTPUT FORMAT (JSON):
{
    "screened_stocks": {
        "hot": [
            {
                "ticker": "SYMBOL",
                "company": "Company Name",
                "score": 9,
                "reasoning": "Why this is hot",
                "priority": 1
            }
        ],
        "warm": [
            {
                "ticker": "SYMBOL",
                "company": "Company Name",
                "score": 6,
                "reasoning": "Why this is warm",
                "concerns": ["Concern 1"]
            }
        ],
        "cold": [
            {
                "ticker": "SYMBOL",
                "company": "Company Name",
                "score": 3,
                "reasoning": "Why we're passing"
            }
        ]
    },
    "total_screened": 25,
    "hot_count": 8,
    "warm_count": 10,
    "cold_count": 7,
    "summary": "Brief screening summary"
}

IMPORTANT:
- Be selective - not everything is HOT
- HOT should be ~30% of input max
- Clear reasoning for each categorization
- Consider the fund mandate if provided
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return False  # Works with provided scout data

    def _build_prompt(self, task: str, context: dict) -> str:
        scout_results = context.get("scout_results", [])
        fund_mandate = context.get("fund_mandate", "")
        themes = context.get("themes", [])

        import json
        scout_data = json.dumps(scout_results, indent=2)

        mandate_note = ""
        if fund_mandate:
            mandate_note = f"\nFund Mandate: {fund_mandate}"

        theme_note = ""
        if themes:
            theme_note = f"\nFund Themes: {', '.join(themes)}"

        return f"""Screen the following stocks from scout output.

=== SCOUT OUTPUT ===
{scout_data}

=== FUND CONTEXT ==={mandate_note}{theme_note}

{task}

Categorize each stock as HOT, WARM, or COLD with clear reasoning.
Return your screening as JSON following the format in your instructions."""


_agent = None


def get_screener_agent() -> ScreenerAgent:
    global _agent
    if _agent is None:
        _agent = ScreenerAgent()
    return _agent
