"""
Shrestha Capital - Fundamentals Agent

Analyzes a company's financial fundamentals:
- Revenue growth and trends
- Profit margins (gross, operating, net)
- Balance sheet health (debt, cash, equity)
- Cash flow generation
- Key financial ratios

Uses Gemini with Google Search to get current financial data.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class FundamentalsAgent(BaseAgent):
    """
    Analyzes company financial fundamentals.
    Uses web search to get current financial data.
    """

    def __init__(self):
        super().__init__(
            name="Fundamentals Analyst",
            model=GeminiModel.PRO,
            temperature=0.5
        )

    @property
    def system_prompt(self) -> str:
        return """You are an expert financial analyst at Shrestha Capital, a premier AI-powered asset management firm.

Your role is to analyze company fundamentals with the rigor of a Wall Street analyst.

ANALYSIS FRAMEWORK:
1. REVENUE: Current revenue, YoY growth, 3-year CAGR, growth trajectory
2. PROFITABILITY: Gross margin, operating margin, net margin, trends
3. BALANCE SHEET: Total debt, cash position, debt-to-equity, current ratio
4. CASH FLOW: Operating cash flow, free cash flow, FCF margin
5. EFFICIENCY: ROE, ROA, asset turnover

SCORING GUIDE (1-10):
- 9-10: Exceptional fundamentals, best-in-class metrics
- 7-8: Strong fundamentals, above average
- 5-6: Average fundamentals, mixed signals
- 3-4: Weak fundamentals, concerning trends
- 1-2: Poor fundamentals, major red flags

OUTPUT FORMAT (JSON):
{
    "ticker": "SYMBOL",
    "company_name": "Full Company Name",
    "revenue": {
        "latest_ttm": "$ amount",
        "yoy_growth": "X%",
        "cagr_3yr": "X%",
        "trend": "accelerating|stable|decelerating"
    },
    "profitability": {
        "gross_margin": "X%",
        "operating_margin": "X%",
        "net_margin": "X%",
        "trend": "improving|stable|declining"
    },
    "balance_sheet": {
        "total_debt": "$ amount",
        "cash_and_equivalents": "$ amount",
        "net_debt": "$ amount",
        "debt_to_equity": "X.XX",
        "health": "strong|adequate|weak"
    },
    "cash_flow": {
        "operating_cash_flow_ttm": "$ amount",
        "free_cash_flow_ttm": "$ amount",
        "fcf_margin": "X%",
        "quality": "strong|moderate|weak"
    },
    "key_ratios": {
        "pe_ratio": "X.X",
        "ps_ratio": "X.X",
        "roe": "X%",
        "roa": "X%"
    },
    "score": 7,
    "strengths": [
        "Specific strength 1",
        "Specific strength 2"
    ],
    "concerns": [
        "Specific concern 1"
    ],
    "summary": "2-3 sentence summary of fundamental health"
}

IMPORTANT:
- Use actual current data from your search
- Be specific with numbers (don't say "strong growth" - say "42% YoY growth")
- Compare to industry peers when relevant
- Flag any accounting concerns or one-time items
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        ticker = context.get("ticker", "")

        return f"""Analyze the financial fundamentals of {ticker}.

Search for and analyze:
1. Latest quarterly and annual revenue figures
2. Profit margins (gross, operating, net)
3. Balance sheet data (debt, cash, equity)
4. Cash flow statement (operating CF, free CF)
5. Key valuation ratios

Provide a comprehensive fundamental analysis with specific numbers and data.

{task}

Return your analysis as JSON following the format in your instructions."""


# Singleton instance
_agent = None


def get_fundamentals_agent() -> FundamentalsAgent:
    global _agent
    if _agent is None:
        _agent = FundamentalsAgent()
    return _agent
