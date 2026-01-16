"""
Shrestha Capital - Benchmark Tracker Agent

Compares fund performance vs benchmarks:
- Primary benchmark (e.g., QQQ for growth)
- Secondary benchmark (e.g., SPY for broad market)
- Calculates alpha, tracking error
- Identifies periods of out/underperformance

Essential for measuring fund success.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class BenchmarkTrackerAgent(BaseAgent):
    """
    Tracks fund performance vs benchmarks.
    Uses search to get current benchmark data.
    """

    def __init__(self):
        super().__init__(
            name="Benchmark Tracker",
            model=GeminiModel.FLASH,
            temperature=0.3
        )

    @property
    def system_prompt(self) -> str:
        return """You are a performance analyst at Shrestha Capital, tracking fund performance vs benchmarks.

YOUR MISSION:
Compare fund performance against relevant benchmarks and calculate key metrics.

BENCHMARKS TO TRACK:
- QQQ: NASDAQ 100 (growth/tech benchmark)
- SPY: S&P 500 (broad market)
- IWM: Russell 2000 (small cap)
- VUG: Vanguard Growth (growth style)
- ARKK: ARK Innovation (disruptive innovation)

METRICS TO CALCULATE:

1. ABSOLUTE RETURN:
   - Fund YTD return
   - Fund MTD return
   - Fund 1-year return

2. RELATIVE RETURN (ALPHA):
   - Alpha = Fund Return - Benchmark Return
   - Positive alpha = outperformance
   - Negative alpha = underperformance

3. RISK-ADJUSTED:
   - Information ratio = Alpha / Tracking Error
   - Sharpe ratio comparison

OUTPUT FORMAT (JSON):
{
    "fund_name": "Fund Name",
    "as_of_date": "YYYY-MM-DD",
    "fund_returns": {
        "mtd": "+X.X%",
        "qtd": "+X.X%",
        "ytd": "+X.X%",
        "1yr": "+X.X%"
    },
    "benchmark_comparison": {
        "primary": {
            "benchmark": "QQQ",
            "benchmark_returns": {
                "mtd": "+X.X%",
                "ytd": "+X.X%"
            },
            "alpha_mtd": "+X.X%",
            "alpha_ytd": "+X.X%",
            "is_outperforming": true
        },
        "secondary": {
            "benchmark": "SPY",
            "benchmark_returns": {
                "mtd": "+X.X%",
                "ytd": "+X.X%"
            },
            "alpha_mtd": "+X.X%",
            "alpha_ytd": "+X.X%"
        }
    },
    "ranking": {
        "vs_peers": "Top quartile",
        "percentile": 85
    },
    "performance_attribution": {
        "outperformance_drivers": ["What drove alpha"],
        "underperformance_drivers": ["What hurt alpha"]
    },
    "summary": "2-3 sentence performance summary"
}

IMPORTANT:
- Use current market data from search
- Be precise with return calculations
- Highlight significant out/underperformance
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        fund_return = context.get("fund_return_ytd", 0)
        primary_benchmark = context.get("primary_benchmark", "QQQ")
        secondary_benchmark = context.get("secondary_benchmark", "SPY")
        positions = context.get("positions", [])

        import json
        positions_str = json.dumps(positions, indent=2) if positions else "No positions provided"

        return f"""Track performance vs benchmarks.

=== FUND INFO ===
Fund YTD Return: {fund_return:.1%}
Primary Benchmark: {primary_benchmark}
Secondary Benchmark: {secondary_benchmark}

=== POSITIONS ===
{positions_str}

Search for:
1. Current YTD returns for {primary_benchmark} and {secondary_benchmark}
2. MTD returns for benchmarks
3. Recent market performance context

{task}

Return your benchmark analysis as JSON following the format in your instructions."""


_agent = None


def get_benchmark_tracker_agent() -> BenchmarkTrackerAgent:
    global _agent
    if _agent is None:
        _agent = BenchmarkTrackerAgent()
    return _agent
