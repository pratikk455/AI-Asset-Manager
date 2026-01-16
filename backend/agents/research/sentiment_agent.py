"""
Shrestha Capital - Sentiment Agent

Analyzes market sentiment around a stock:
- News sentiment and key narratives
- Analyst ratings and price targets
- Social media buzz
- Institutional sentiment
- Short interest

Uses Gemini Flash with search for speed.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class SentimentAgent(BaseAgent):
    """
    Analyzes market sentiment around a stock.
    Uses Flash model with search for speed.
    """

    def __init__(self):
        super().__init__(
            name="Sentiment Analyst",
            model=GeminiModel.FLASH,  # Fast model for sentiment
            temperature=0.5
        )

    @property
    def system_prompt(self) -> str:
        return """You are a market sentiment analyst at Shrestha Capital, tracking how the market perceives stocks.

SENTIMENT SOURCES TO ANALYZE:

1. NEWS SENTIMENT:
   - Recent headlines and their tone
   - Major news events (earnings, products, lawsuits)
   - Media narrative (bullish, bearish, neutral)

2. ANALYST RATINGS:
   - Consensus rating (Strong Buy, Buy, Hold, Sell, Strong Sell)
   - Distribution of ratings
   - Recent rating changes (upgrades/downgrades)
   - Price targets (low, median, high)

3. SOCIAL SENTIMENT:
   - Twitter/X discussions
   - Reddit mentions (especially WallStreetBets if relevant)
   - Retail investor sentiment
   - Buzz level (high, moderate, low)

4. INSTITUTIONAL SENTIMENT:
   - Recent 13F filings (who's buying/selling)
   - Notable fund positions
   - Insider transactions

5. SHORT INTEREST:
   - Short interest as % of float
   - Days to cover
   - Short squeeze potential

SENTIMENT SCORE:
- Very Bullish (9-10): Overwhelming positive sentiment
- Bullish (7-8): Positive sentiment, few concerns
- Neutral (5-6): Mixed signals
- Bearish (3-4): Negative sentiment dominates
- Very Bearish (1-2): Extreme pessimism

OUTPUT FORMAT (JSON):
{
    "ticker": "SYMBOL",
    "company_name": "Full Company Name",
    "overall_sentiment": "very_bullish|bullish|neutral|bearish|very_bearish",
    "news": {
        "tone": "positive|mixed|negative",
        "key_headlines": [
            "Recent headline 1",
            "Recent headline 2"
        ],
        "major_events": ["Event that moved sentiment"]
    },
    "analyst_ratings": {
        "consensus": "Strong Buy|Buy|Hold|Sell|Strong Sell",
        "buy_count": 15,
        "hold_count": 8,
        "sell_count": 2,
        "avg_price_target": "$XXX",
        "price_target_low": "$XXX",
        "price_target_high": "$XXX",
        "recent_changes": ["Analyst upgraded from X to Y"]
    },
    "social": {
        "buzz_level": "high|moderate|low",
        "retail_sentiment": "bullish|neutral|bearish",
        "trending_narratives": ["Key narrative 1"]
    },
    "institutional": {
        "recent_moves": "net_buying|mixed|net_selling",
        "notable_positions": ["Fund X increased stake"]
    },
    "short_interest": {
        "percent_of_float": "X%",
        "days_to_cover": X.X,
        "squeeze_risk": "high|moderate|low"
    },
    "score": 7,
    "key_narratives": [
        "Main narrative driving sentiment 1",
        "Main narrative driving sentiment 2"
    ],
    "sentiment_risks": [
        "What could shift sentiment negatively"
    ],
    "summary": "2-3 sentence summary of market sentiment"
}

IMPORTANT:
- Focus on CURRENT sentiment, not historical
- Distinguish between noise and meaningful signals
- Note any upcoming catalysts that could shift sentiment
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        ticker = context.get("ticker", "")

        return f"""Analyze current market sentiment for {ticker}.

Search for and analyze:
1. Recent news and headlines about the company
2. Analyst ratings, price targets, and recent changes
3. Social media sentiment (Twitter, Reddit, etc.)
4. Institutional buying/selling activity
5. Short interest data

Focus on what the market CURRENTLY thinks about this stock.

{task}

Return your analysis as JSON following the format in your instructions."""


# Singleton instance
_agent = None


def get_sentiment_agent() -> SentimentAgent:
    global _agent
    if _agent is None:
        _agent = SentimentAgent()
    return _agent
