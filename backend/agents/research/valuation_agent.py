"""
Shrestha Capital - Valuation Agent

Analyzes stock valuation:
- Current price and market cap
- Valuation multiples (P/E, P/S, EV/EBITDA, etc.)
- Historical valuation ranges
- Peer comparison
- Fair value estimate
- Upside/downside potential

Uses Gemini Pro with search for rigorous analysis.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class ValuationAgent(BaseAgent):
    """
    Analyzes stock valuation and estimates fair value.
    Uses Pro model with search for rigorous analysis.
    """

    def __init__(self):
        super().__init__(
            name="Valuation Analyst",
            model=GeminiModel.PRO,
            temperature=0.5
        )

    @property
    def system_prompt(self) -> str:
        return """You are a valuation specialist at Shrestha Capital, determining whether stocks are fairly priced.

VALUATION FRAMEWORK:

1. CURRENT VALUATION MULTIPLES:
   - P/E Ratio (TTM and Forward)
   - P/S Ratio (Price to Sales)
   - EV/EBITDA
   - EV/Revenue
   - P/B Ratio (if relevant)
   - PEG Ratio

2. HISTORICAL CONTEXT:
   - Current vs 5-year average multiples
   - Is it at highs, lows, or middle of range?
   - What drove historical peaks/troughs?

3. PEER COMPARISON:
   - How does it compare to direct competitors?
   - Premium or discount to peers?
   - Is the premium/discount justified?

4. ANALYST TARGETS:
   - Wall Street consensus price target
   - Range of targets (bull to bear)
   - Implied upside/downside

5. FAIR VALUE ESTIMATE:
   - Your estimate of intrinsic value
   - Methodology used (DCF, multiple-based, etc.)
   - Key assumptions

VALUATION VERDICT:
- Significantly Undervalued: 30%+ upside
- Undervalued: 15-30% upside
- Fairly Valued: Within 15% of fair value
- Overvalued: 15-30% downside
- Significantly Overvalued: 30%+ downside

OUTPUT FORMAT (JSON):
{
    "ticker": "SYMBOL",
    "company_name": "Full Company Name",
    "current_price": "$XXX.XX",
    "market_cap": "$XXX billion",
    "enterprise_value": "$XXX billion",
    "multiples": {
        "pe_ttm": XX.X,
        "pe_forward": XX.X,
        "ps_ratio": XX.X,
        "ev_ebitda": XX.X,
        "ev_revenue": XX.X,
        "peg_ratio": X.XX
    },
    "historical_context": {
        "pe_5yr_avg": XX.X,
        "current_vs_history": "above_average|average|below_average",
        "percentile": "Xth percentile of 5-year range"
    },
    "peer_comparison": {
        "peers": [
            {"ticker": "PEER1", "pe": XX.X, "ps": XX.X},
            {"ticker": "PEER2", "pe": XX.X, "ps": XX.X}
        ],
        "vs_peers": "premium|inline|discount",
        "premium_discount_pct": "+X% or -X%"
    },
    "analyst_targets": {
        "consensus_target": "$XXX",
        "target_low": "$XXX",
        "target_high": "$XXX",
        "implied_upside": "+X%"
    },
    "fair_value_estimate": {
        "value": "$XXX",
        "methodology": "Multiple-based / DCF / etc.",
        "key_assumptions": [
            "Assumption 1",
            "Assumption 2"
        ],
        "upside_to_fair_value": "+X%"
    },
    "verdict": "undervalued|fairly_valued|overvalued",
    "score": 7,
    "valuation_risks": [
        "What could make current valuation wrong"
    ],
    "summary": "2-3 sentence summary of valuation"
}

IMPORTANT:
- Use current market data
- Be specific with numbers
- Consider growth rate when evaluating multiples
- High multiples can be justified if growth is exceptional
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        ticker = context.get("ticker", "")

        return f"""Analyze the valuation of {ticker}.

Search for and analyze:
1. Current stock price and market cap
2. Valuation multiples (P/E, P/S, EV/EBITDA, PEG, etc.)
3. Historical valuation ranges
4. Peer company valuations for comparison
5. Analyst price targets
6. Growth rates to contextualize multiples

Determine whether the stock is undervalued, fairly valued, or overvalued.

{task}

Return your analysis as JSON following the format in your instructions."""


# Singleton instance
_agent = None


def get_valuation_agent() -> ValuationAgent:
    global _agent
    if _agent is None:
        _agent = ValuationAgent()
    return _agent
