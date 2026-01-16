"""
Test the full discovery → analysis flow
"""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from orchestrator.pipelines.scout_pipeline import ScoutPipeline
from orchestrator.pipelines.analysis_pipeline import analyze_stock


async def main():
    print("\n" + "="*70)
    print("SHRESTHA CAPITAL - Full Discovery → Analysis Flow Test")
    print("="*70 + "\n")

    # Step 1: Quick discovery for AI theme
    print("STEP 1: Scout for AI stocks\n")
    pipeline = ScoutPipeline()

    discovery = await pipeline.quick_discover("AI / Machine Learning")

    stocks = discovery.get("stocks", [])
    print(f"\nFound {len(stocks)} AI stocks:")
    for i, stock in enumerate(stocks[:5], 1):  # Show top 5
        print(f"  {i}. {stock.get('ticker', 'N/A')} - {stock.get('company', 'N/A')}")

    if not stocks:
        print("No stocks found. Exiting.")
        return

    # Step 2: Pick the first stock and analyze it
    first_stock = stocks[0]
    ticker = first_stock.get("ticker", "NVDA")

    print(f"\n{'='*70}")
    print(f"STEP 2: Analyze {ticker}")
    print("="*70 + "\n")

    analysis = await analyze_stock(ticker)

    thesis = analysis.get("thesis", {})

    print("\n" + "="*70)
    print("INVESTMENT THESIS")
    print("="*70 + "\n")

    print(f"Ticker: {ticker}")
    print(f"Recommendation: {thesis.get('recommendation', 'N/A').upper()}")
    print(f"Conviction: {thesis.get('conviction', 0):.0%}")
    print(f"Target Weight: {(thesis.get('target_weight') or 0):.1%}")

    print("\n--- THESIS SUMMARY ---")
    print(thesis.get('thesis_summary', 'N/A'))

    print("\n--- SCORES ---")
    scores = thesis.get('score_breakdown', {})
    print(f"  Fundamentals: {scores.get('fundamentals', 'N/A')}/10")
    print(f"  Moat:         {scores.get('moat', 'N/A')}/10")
    print(f"  Sentiment:    {scores.get('sentiment', 'N/A')}/10")
    print(f"  Valuation:    {scores.get('valuation', 'N/A')}/10")
    print(f"  Overall:      {scores.get('overall', 'N/A')}/10")

    # Save result
    output_file = f"full_flow_{ticker}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "discovery": discovery,
            "analysis": analysis
        }, f, indent=2)

    print(f"\n✓ Full result saved to {output_file}")

    print("\n" + "="*70)
    print("FLOW COMPLETE!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
