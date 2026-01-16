"""
Shrestha Capital - Emerging Leaders Scout

Finds small-to-mid cap companies ($1B-$50B) with high growth:
- 30%+ revenue growth
- Category leaders in their niche
- Expanding addressable market
- Strong competitive position

These are the "future large caps" - companies early in their growth curve.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class EmergingLeadersScout(BaseAgent):
    """
    Scouts for emerging leader stocks - fast-growing mid caps.
    Uses web search to find current high-growth companies.
    """

    def __init__(self):
        super().__init__(
            name="Emerging Leaders Scout",
            model=GeminiModel.FLASH,
            temperature=0.6
        )

    @property
    def system_prompt(self) -> str:
        return """You are a growth stock scout at Shrestha Capital, specializing in finding emerging leaders.

YOUR MISSION:
Find small-to-mid cap companies ($1B-$50B market cap) that are:
- Growing revenue 30%+ annually
- Leaders in their category/niche
- Benefiting from large and expanding markets
- Building competitive moats

TARGET PROFILE:
- Market Cap: $1B - $50B
- Revenue Growth: 30%+ YoY
- Category Position: #1 or #2 in their niche
- Market Opportunity: Large TAM, early penetration
- Business Model: Scalable, high gross margins preferred

WHERE TO LOOK:
- SaaS/Cloud software leaders
- Fintech disruptors
- Healthcare innovators
- E-commerce winners
- Cybersecurity leaders
- Data/Analytics platforms

AVOID:
- Unprofitable companies with no path to profitability
- One-hit wonders (single product, no expansion)
- Companies in declining markets
- Overly promotional/hype stocks

OUTPUT FORMAT (JSON):
{
    "stocks": [
        {
            "ticker": "SYMBOL",
            "company": "Full Company Name",
            "market_cap": "$X billion",
            "revenue_growth": "XX%",
            "category": "What they do",
            "why_picked": "2-3 sentence thesis on why this is an emerging leader",
            "signal": "What caught your attention"
        }
    ],
    "total_found": 10,
    "sectors_covered": ["SaaS", "Fintech", ...],
    "summary": "Brief summary of the scout's findings"
}

IMPORTANT:
- Find 8-12 stocks per scout run
- Use current data from your search
- Focus on QUALITY over quantity
- Each pick should have a clear growth thesis
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        sectors = context.get("sectors", [])
        exclude = context.get("exclude", [])

        sector_focus = ""
        if sectors:
            sector_focus = f"\nFocus on these sectors: {', '.join(sectors)}"

        exclude_note = ""
        if exclude:
            exclude_note = f"\nExclude these tickers (already owned): {', '.join(exclude)}"

        return f"""Scout for emerging leader stocks.

Search for:
1. Fast-growing mid-cap companies ($1B-$50B market cap)
2. Companies with 30%+ revenue growth
3. Category leaders in expanding markets
4. Recent IPOs or companies that have emerged as leaders
{sector_focus}
{exclude_note}

{task}

Return your findings as JSON following the format in your instructions."""


_agent = None


def get_emerging_leaders_scout() -> EmergingLeadersScout:
    global _agent
    if _agent is None:
        _agent = EmergingLeadersScout()
    return _agent
