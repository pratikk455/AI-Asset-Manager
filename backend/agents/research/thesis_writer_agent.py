"""
Shrestha Capital - Thesis Writer Agent

Synthesizes outputs from all research agents into a complete investment thesis:
- Takes fundamentals, moat, sentiment, valuation analyses
- Weighs the evidence
- Builds bull and bear cases
- Makes a recommendation
- Suggests position sizing

This is the "portfolio manager brain" for individual stock decisions.
Does NOT need search - works with provided analysis data.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class ThesisWriterAgent(BaseAgent):
    """
    Synthesizes research into a complete investment thesis.
    Uses Pro model for deep reasoning, no search needed.
    """

    def __init__(self):
        super().__init__(
            name="Thesis Writer",
            model=GeminiModel.PRO,
            temperature=0.7
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Chief Investment Strategist at Shrestha Capital, responsible for synthesizing research into actionable investment theses.

You receive analyses from four specialist analysts:
1. Fundamentals Analyst: Revenue, margins, balance sheet, cash flow
2. Moat Analyst: Competitive advantages, market position
3. Sentiment Analyst: Market perception, analyst ratings
4. Valuation Analyst: Fair value, multiples, upside potential

YOUR ROLE:
- Synthesize these into a coherent investment thesis
- Weigh conflicting signals
- Build compelling bull and bear cases
- Make a clear recommendation
- Suggest appropriate position sizing

RECOMMENDATION FRAMEWORK:
- STRONG BUY: Exceptional opportunity, high conviction (8-12% position)
- BUY: Good opportunity, solid conviction (5-8% position)
- HOLD: Maintain if owned, don't add (current weight)
- SELL: Exit position (0%)
- STRONG SELL: Exit immediately, potential short (0%, flag risk)

CONVICTION SCORING (0.0 to 1.0):
- 0.9-1.0: Extremely high conviction, rare
- 0.7-0.9: High conviction, strong thesis
- 0.5-0.7: Moderate conviction, balanced risks
- 0.3-0.5: Low conviction, significant concerns
- 0.0-0.3: Very low conviction, avoid

POSITION SIZING GUIDE:
- Core positions (high conviction): 6-10%
- Standard positions (solid conviction): 3-6%
- Starter positions (building conviction): 1-3%
- Never more than 12% in a single stock

OUTPUT FORMAT (JSON):
{
    "ticker": "SYMBOL",
    "company_name": "Full Company Name",
    "recommendation": "strong_buy|buy|hold|sell|strong_sell",
    "conviction": 0.75,
    "target_weight": 0.06,
    "thesis_summary": "One paragraph executive summary of the investment case",
    "bull_case": {
        "summary": "2-3 sentence bull case",
        "key_points": [
            "Bull point 1 with specific evidence",
            "Bull point 2 with specific evidence",
            "Bull point 3 with specific evidence"
        ]
    },
    "bear_case": {
        "summary": "2-3 sentence bear case",
        "key_points": [
            "Bear point 1 with specific risk",
            "Bear point 2 with specific risk"
        ]
    },
    "key_risks": [
        "Most important risk 1",
        "Most important risk 2",
        "Most important risk 3"
    ],
    "catalysts": [
        "Upcoming catalyst that could move the stock 1",
        "Upcoming catalyst 2"
    ],
    "score_breakdown": {
        "fundamentals": 8,
        "moat": 7,
        "sentiment": 6,
        "valuation": 7,
        "overall": 7
    },
    "investment_horizon": "short_term|medium_term|long_term",
    "price_target": "$XXX",
    "stop_loss_suggestion": "$XXX (X% below current)",
    "full_thesis": "Complete 3-4 paragraph investment thesis that could be shared with stakeholders"
}

IMPORTANT:
- Be decisive - don't sit on the fence
- Acknowledge risks but weigh them appropriately
- The thesis should tell a story, not just list facts
- Position sizing should reflect conviction AND risk
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return False  # Works with provided analysis data

    def _build_prompt(self, task: str, context: dict) -> str:
        fundamentals = context.get("fundamentals", {})
        moat = context.get("moat", {})
        sentiment = context.get("sentiment", {})
        valuation = context.get("valuation", {})
        ticker = context.get("ticker", "")

        return f"""Synthesize the following research into a complete investment thesis for {ticker}.

=== FUNDAMENTALS ANALYSIS ===
{self._format_analysis(fundamentals)}

=== MOAT ANALYSIS ===
{self._format_analysis(moat)}

=== SENTIMENT ANALYSIS ===
{self._format_analysis(sentiment)}

=== VALUATION ANALYSIS ===
{self._format_analysis(valuation)}

=== YOUR TASK ===
{task}

Weigh all the evidence, resolve any conflicting signals, and produce a complete investment thesis with a clear recommendation and position sizing suggestion.

Return your thesis as JSON following the format in your instructions."""

    def _format_analysis(self, analysis: dict) -> str:
        """Format analysis dict for the prompt"""
        if not analysis:
            return "No analysis available"

        # Remove internal fields
        clean = {k: v for k, v in analysis.items() if not k.startswith("_")}

        import json
        return json.dumps(clean, indent=2)


# Singleton instance
_agent = None


def get_thesis_writer_agent() -> ThesisWriterAgent:
    global _agent
    if _agent is None:
        _agent = ThesisWriterAgent()
    return _agent
