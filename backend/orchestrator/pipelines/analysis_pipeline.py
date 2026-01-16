"""
Shrestha Capital - Stock Analysis Pipeline

Orchestrates the complete analysis of a single stock:
1. Run 4 research agents in parallel (fundamentals, moat, sentiment, valuation)
2. Collect all outputs
3. Pass to thesis writer for synthesis
4. Return complete thesis

This is the core "analyze a stock" workflow.
"""

import asyncio
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.research.fundamentals_agent import get_fundamentals_agent
from agents.research.moat_agent import get_moat_agent
from agents.research.sentiment_agent import get_sentiment_agent
from agents.research.valuation_agent import get_valuation_agent
from agents.research.thesis_writer_agent import get_thesis_writer_agent


class AnalysisPipeline:
    """
    Orchestrates complete stock analysis.

    Usage:
        pipeline = AnalysisPipeline()
        thesis = await pipeline.analyze("TSLA")
    """

    def __init__(self):
        self.fundamentals_agent = get_fundamentals_agent()
        self.moat_agent = get_moat_agent()
        self.sentiment_agent = get_sentiment_agent()
        self.valuation_agent = get_valuation_agent()
        self.thesis_writer = get_thesis_writer_agent()

    async def analyze(self, ticker: str, additional_context: Optional[str] = None) -> dict:
        """
        Run complete analysis on a stock.

        Args:
            ticker: Stock ticker symbol (e.g., "TSLA")
            additional_context: Optional extra context for the analysis

        Returns:
            Complete thesis dict with all analysis
        """
        print(f"\n{'='*60}")
        print(f"ANALYZING: {ticker}")
        print(f"{'='*60}\n")

        # Step 1: Run all research agents in parallel
        print("Step 1: Running research agents in parallel...")

        research_tasks = [
            self._run_agent("Fundamentals", self.fundamentals_agent, ticker),
            self._run_agent("Moat", self.moat_agent, ticker),
            self._run_agent("Sentiment", self.sentiment_agent, ticker),
            self._run_agent("Valuation", self.valuation_agent, ticker),
        ]

        results = await asyncio.gather(*research_tasks, return_exceptions=True)

        # Collect results
        fundamentals, moat, sentiment, valuation = results

        # Handle any errors
        for name, result in [
            ("Fundamentals", fundamentals),
            ("Moat", moat),
            ("Sentiment", sentiment),
            ("Valuation", valuation)
        ]:
            if isinstance(result, Exception):
                print(f"  ⚠️  {name} agent failed: {str(result)}")

        # Step 2: Synthesize with thesis writer
        print("\nStep 2: Synthesizing thesis...")

        context = {
            "ticker": ticker,
            "fundamentals": fundamentals if not isinstance(fundamentals, Exception) else {},
            "moat": moat if not isinstance(moat, Exception) else {},
            "sentiment": sentiment if not isinstance(sentiment, Exception) else {},
            "valuation": valuation if not isinstance(valuation, Exception) else {},
        }

        task = f"Create a complete investment thesis for {ticker}."
        if additional_context:
            task += f" Additional context: {additional_context}"

        thesis = await self.thesis_writer.run(task, context)

        print("  ✓ Thesis complete")

        # Step 3: Combine all data
        result = {
            "ticker": ticker,
            "thesis": thesis,
            "research": {
                "fundamentals": fundamentals if not isinstance(fundamentals, Exception) else {"_error": str(fundamentals)},
                "moat": moat if not isinstance(moat, Exception) else {"_error": str(moat)},
                "sentiment": sentiment if not isinstance(sentiment, Exception) else {"_error": str(sentiment)},
                "valuation": valuation if not isinstance(valuation, Exception) else {"_error": str(valuation)},
            },
            "sources": self._collect_sources(fundamentals, moat, sentiment, valuation)
        }

        print(f"\n{'='*60}")
        print(f"ANALYSIS COMPLETE: {ticker}")
        print(f"Recommendation: {thesis.get('recommendation', 'N/A')}")
        print(f"Conviction: {thesis.get('conviction', 'N/A')}")
        print(f"Target Weight: {thesis.get('target_weight', 'N/A')}")
        print(f"{'='*60}\n")

        return result

    async def _run_agent(self, name: str, agent, ticker: str) -> dict:
        """Run a single agent and return result"""
        print(f"  → Running {name} agent...")
        try:
            result = await agent.run(
                task=f"Analyze {ticker}",
                context={"ticker": ticker}
            )
            print(f"  ✓ {name} complete (score: {result.get('score', 'N/A')})")
            return result
        except Exception as e:
            print(f"  ✗ {name} failed: {str(e)}")
            raise

    def _collect_sources(self, *analyses) -> list:
        """Collect all sources from analyses"""
        sources = []
        for analysis in analyses:
            if isinstance(analysis, dict) and "_sources" in analysis:
                sources.extend(analysis["_sources"])
        return sources


# Convenience function
async def analyze_stock(ticker: str, additional_context: Optional[str] = None) -> dict:
    """Analyze a stock using the full pipeline"""
    pipeline = AnalysisPipeline()
    return await pipeline.analyze(ticker, additional_context)
