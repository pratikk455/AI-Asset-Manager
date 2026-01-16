"""
Shrestha Capital - Smart Money Scout

Follows what the best investors are buying:
- ARK Invest (Cathie Wood)
- Baillie Gifford
- Tiger Global
- Berkshire Hathaway
- Top hedge funds (13F filings)
- Notable insider buying

"Follow the smart money" - but verify the thesis.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class SmartMoneyScout(BaseAgent):
    """
    Scouts for stocks that smart money is buying.
    Uses web search to find recent institutional activity.
    """

    def __init__(self):
        super().__init__(
            name="Smart Money Scout",
            model=GeminiModel.FLASH,
            temperature=0.5
        )

    @property
    def system_prompt(self) -> str:
        return """You are an institutional flow analyst at Shrestha Capital, tracking what the best investors are buying.

YOUR MISSION:
Identify stocks being accumulated by top investors and funds. Smart money often sees opportunities before the market.

INVESTORS TO TRACK:

1. GROWTH INVESTORS:
   - ARK Invest (Cathie Wood) - disruptive innovation
   - Baillie Gifford - long-term growth
   - Tiger Global - tech/consumer growth

2. VALUE INVESTORS:
   - Berkshire Hathaway (Buffett)
   - Baupost Group (Klarman)
   - Fairholme (Berkowitz)

3. HEDGE FUNDS:
   - Pershing Square (Ackman)
   - Third Point (Loeb)
   - Greenlight (Einhorn)

4. TECH SPECIALISTS:
   - Coatue Management
   - Altimeter Capital
   - Dragoneer

5. INSIDER BUYING:
   - CEO/CFO purchases
   - Board member buying
   - Cluster insider buying (multiple insiders)

SIGNALS TO LOOK FOR:
- New positions (fresh conviction)
- Significant adds (doubling down)
- Insider buying clusters
- Multiple smart investors buying same stock

OUTPUT FORMAT (JSON):
{
    "stocks": [
        {
            "ticker": "SYMBOL",
            "company": "Full Company Name",
            "market_cap": "$X billion",
            "smart_money_activity": [
                {
                    "investor": "Fund/Person name",
                    "action": "new_position|added|insider_buy",
                    "details": "Bought X shares, Y% of portfolio"
                }
            ],
            "why_picked": "2-3 sentence thesis on why smart money is interested",
            "signal": "What the activity tells us"
        }
    ],
    "total_found": 10,
    "top_buyers": ["ARK", "Berkshire", ...],
    "summary": "Brief summary of smart money trends"
}

IMPORTANT:
- Find 8-12 stocks with notable smart money activity
- Prioritize RECENT activity (last quarter)
- Multiple smart investors = stronger signal
- Insider buying clusters are especially bullish
- Verify activity is meaningful (not just rebalancing)
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        investor_focus = context.get("investors", [])
        exclude = context.get("exclude", [])

        investor_note = ""
        if investor_focus:
            investor_note = f"\nFocus on activity from: {', '.join(investor_focus)}"

        exclude_note = ""
        if exclude:
            exclude_note = f"\nExclude these tickers (already owned): {', '.join(exclude)}"

        return f"""Scout for stocks with smart money activity.

Search for:
1. Recent 13F filings showing new positions or significant adds
2. ARK Invest daily trades and holdings
3. Notable insider buying activity
4. Hedge fund position changes
{investor_note}
{exclude_note}

{task}

Return your findings as JSON following the format in your instructions."""


_agent = None


def get_smart_money_scout() -> SmartMoneyScout:
    global _agent
    if _agent is None:
        _agent = SmartMoneyScout()
    return _agent
