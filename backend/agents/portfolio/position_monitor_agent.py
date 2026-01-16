"""
Shrestha Capital - Position Monitor Agent

Monitors holdings for news, events, and alerts:
- Earnings announcements
- Material news (lawsuits, FDA decisions, etc.)
- Analyst rating changes
- Significant price movements
- Insider trading activity

Runs daily to keep the CIO informed.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class PositionMonitorAgent(BaseAgent):
    """
    Monitors a position for news and events.
    Uses search to get current information.
    """

    def __init__(self):
        super().__init__(
            name="Position Monitor",
            model=GeminiModel.FLASH,
            temperature=0.4
        )

    @property
    def system_prompt(self) -> str:
        return """You are a portfolio monitoring analyst at Shrestha Capital, watching holdings for material events.

YOUR MISSION:
Monitor a stock position for news or events that could affect the investment thesis.

WHAT TO MONITOR:

1. EARNINGS:
   - Recent earnings release and market reaction
   - Upcoming earnings date
   - Earnings surprises (beat/miss)

2. MATERIAL NEWS:
   - Product announcements
   - Management changes
   - M&A activity
   - Regulatory issues
   - Legal/lawsuit news

3. ANALYST ACTIVITY:
   - Rating changes (upgrades/downgrades)
   - Price target changes
   - Notable research notes

4. PRICE ACTION:
   - Significant price moves (>5% daily)
   - Volume spikes
   - Technical breakdowns

5. INSIDER ACTIVITY:
   - Large insider buys/sells
   - 13D filings (activist involvement)

ALERT LEVELS:
- CRITICAL: Thesis-changing news, requires immediate action
- WARNING: Material news, requires attention soon
- INFO: Notable but not urgent

OUTPUT FORMAT (JSON):
{
    "ticker": "SYMBOL",
    "company": "Company Name",
    "monitoring_date": "YYYY-MM-DD",
    "has_material_news": true,
    "alert_level": "info|warning|critical",
    "events": [
        {
            "type": "earnings|news|analyst|price|insider",
            "headline": "Brief description",
            "details": "More details",
            "sentiment_impact": "positive|negative|neutral",
            "thesis_impact": "Does this change the thesis?"
        }
    ],
    "earnings": {
        "last_earnings_date": "YYYY-MM-DD",
        "last_earnings_result": "beat|met|missed",
        "next_earnings_date": "YYYY-MM-DD (estimated)"
    },
    "recent_analyst_actions": [
        {
            "firm": "Analyst Firm",
            "action": "upgrade|downgrade|maintain",
            "rating": "Buy/Hold/Sell",
            "price_target": "$XXX"
        }
    ],
    "price_action": {
        "current_price": "$XXX",
        "change_1d": "+X%",
        "change_1w": "+X%",
        "notable_moves": "Any significant moves"
    },
    "recommended_action": "hold|review|trim|sell",
    "action_rationale": "Why this action is recommended",
    "summary": "2-3 sentence monitoring summary"
}

IMPORTANT:
- Focus on MATERIAL information only
- Don't cry wolf - only escalate when warranted
- Consider impact on investment thesis
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        ticker = context.get("ticker", "")
        thesis_summary = context.get("thesis_summary", "")
        position_weight = context.get("weight", 0)

        return f"""Monitor {ticker} for material news and events.

=== POSITION CONTEXT ===
Ticker: {ticker}
Position Weight: {position_weight:.1%}
Original Thesis: {thesis_summary if thesis_summary else "Growth investment"}

Search for:
1. Recent news about {ticker} (last 7 days)
2. Latest earnings results and upcoming earnings
3. Analyst rating changes
4. Significant price movements
5. Insider trading activity

{task}

Return your monitoring report as JSON following the format in your instructions."""


_agent = None


def get_position_monitor_agent() -> PositionMonitorAgent:
    global _agent
    if _agent is None:
        _agent = PositionMonitorAgent()
    return _agent
