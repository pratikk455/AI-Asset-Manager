"""
Shrestha Capital - Scout Pipeline

Orchestrates stock discovery:
1. Run multiple scouts in parallel (based on fund themes)
2. Aggregate and deduplicate results
3. Screen stocks into HOT/WARM/COLD
4. Return prioritized universe for analysis

This feeds into the analysis pipeline.
"""

import asyncio
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.scouts.emerging_leaders_scout import get_emerging_leaders_scout
from agents.scouts.disruption_scout import get_disruption_scout
from agents.scouts.thematic_scout import get_thematic_scout
from agents.scouts.smart_money_scout import get_smart_money_scout
from agents.research.screener_agent import get_screener_agent


class ScoutPipeline:
    """
    Orchestrates stock discovery through multiple scouts.

    Usage:
        pipeline = ScoutPipeline()
        universe = await pipeline.discover(
            themes=["AI", "Fintech"],
            mandate="US Growth"
        )
    """

    def __init__(self):
        self.emerging_scout = get_emerging_leaders_scout()
        self.disruption_scout = get_disruption_scout()
        self.thematic_scout = get_thematic_scout()
        self.smart_money_scout = get_smart_money_scout()
        self.screener = get_screener_agent()

    async def discover(
        self,
        themes: Optional[List[str]] = None,
        mandate: Optional[str] = None,
        exclude_tickers: Optional[List[str]] = None,
        run_all_scouts: bool = False
    ) -> dict:
        """
        Run discovery to build a stock universe.

        Args:
            themes: Specific themes to scout (e.g., ["AI", "Fintech"])
            mandate: Fund mandate for context
            exclude_tickers: Already-owned tickers to exclude
            run_all_scouts: Run all scouts regardless of themes

        Returns:
            Screened universe with HOT/WARM/COLD categorization
        """
        print(f"\n{'='*60}")
        print("SCOUT PIPELINE: Building Stock Universe")
        print(f"{'='*60}\n")

        exclude = exclude_tickers or []
        themes = themes or []

        # Step 1: Determine which scouts to run
        scout_tasks = []

        # Always run emerging leaders and smart money
        scout_tasks.append(
            self._run_scout("Emerging Leaders", self.emerging_scout, {
                "exclude": exclude
            })
        )
        scout_tasks.append(
            self._run_scout("Smart Money", self.smart_money_scout, {
                "exclude": exclude
            })
        )

        # Run disruption scout if mandate suggests it
        if run_all_scouts or "growth" in (mandate or "").lower() or "disruption" in (mandate or "").lower():
            scout_tasks.append(
                self._run_scout("Disruption", self.disruption_scout, {
                    "exclude": exclude
                })
            )

        # Run thematic scout for each theme
        for theme in themes:
            scout_tasks.append(
                self._run_scout(f"Thematic ({theme})", self.thematic_scout, {
                    "theme": theme,
                    "exclude": exclude
                })
            )

        # Step 2: Run scouts in parallel
        print(f"Running {len(scout_tasks)} scouts in parallel...\n")
        results = await asyncio.gather(*scout_tasks, return_exceptions=True)

        # Step 3: Aggregate results
        all_stocks = []
        scout_summaries = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"  ⚠️  Scout failed: {str(result)[:100]}")
                continue

            scout_name = result.get("_scout_name", f"Scout {i}")
            stocks = result.get("stocks", [])

            print(f"  ✓ {scout_name}: found {len(stocks)} stocks")
            scout_summaries.append({
                "name": scout_name,
                "count": len(stocks),
                "summary": result.get("summary", "")
            })

            for stock in stocks:
                stock["_source"] = scout_name
                all_stocks.append(stock)

        # Step 4: Deduplicate by ticker
        seen_tickers = set()
        unique_stocks = []
        for stock in all_stocks:
            ticker = stock.get("ticker", "")
            if ticker and ticker not in seen_tickers:
                seen_tickers.add(ticker)
                unique_stocks.append(stock)
            elif ticker in seen_tickers:
                # Multiple scouts found same stock - boost signal
                for s in unique_stocks:
                    if s.get("ticker") == ticker:
                        s["_multi_scout"] = True
                        break

        print(f"\n  Total unique stocks: {len(unique_stocks)}")

        # Step 5: Screen stocks
        print("\nScreening stocks...\n")
        screened = await self.screener.run(
            task="Screen these stocks for investment potential",
            context={
                "scout_results": unique_stocks,
                "fund_mandate": mandate,
                "themes": themes
            }
        )

        print(f"  HOT:  {screened.get('hot_count', 0)} stocks")
        print(f"  WARM: {screened.get('warm_count', 0)} stocks")
        print(f"  COLD: {screened.get('cold_count', 0)} stocks")

        # Step 6: Build final output
        result = {
            "universe": screened.get("screened_stocks", {}),
            "stats": {
                "scouts_run": len(scout_tasks),
                "total_discovered": len(all_stocks),
                "unique_stocks": len(unique_stocks),
                "hot_count": screened.get("hot_count", 0),
                "warm_count": screened.get("warm_count", 0),
                "cold_count": screened.get("cold_count", 0),
            },
            "scout_summaries": scout_summaries,
            "screening_summary": screened.get("summary", "")
        }

        print(f"\n{'='*60}")
        print("SCOUT PIPELINE COMPLETE")
        print(f"{'='*60}\n")

        return result

    async def _run_scout(self, name: str, scout, context: dict) -> dict:
        """Run a single scout"""
        print(f"  → Running {name} scout...")
        try:
            result = await scout.run(
                task=f"Find investment opportunities",
                context=context
            )
            result["_scout_name"] = name
            return result
        except Exception as e:
            print(f"  ✗ {name} failed: {str(e)[:100]}")
            raise

    async def quick_discover(self, theme: str) -> dict:
        """
        Quick discovery for a single theme.
        Useful for targeted searches.
        """
        print(f"\nQuick scout for theme: {theme}\n")

        result = await self.thematic_scout.run(
            task=f"Find the best stocks for {theme}",
            context={"theme": theme}
        )

        return {
            "theme": theme,
            "stocks": result.get("stocks", []),
            "summary": result.get("summary", "")
        }


# Convenience function
async def discover_stocks(
    themes: Optional[List[str]] = None,
    mandate: Optional[str] = None,
    exclude: Optional[List[str]] = None
) -> dict:
    """Discover stocks using the scout pipeline"""
    pipeline = ScoutPipeline()
    return await pipeline.discover(themes, mandate, exclude)
