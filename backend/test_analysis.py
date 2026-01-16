"""
Test the full analysis pipeline on Tesla (TSLA)
"""

import asyncio
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from orchestrator.pipelines.analysis_pipeline import analyze_stock


async def main():
    print("\n" + "="*70)
    print("SHRESTHA CAPITAL - Stock Analysis Pipeline Test")
    print("="*70 + "\n")

    # Analyze Tesla
    ticker = "TSLA"

    try:
        result = await analyze_stock(ticker)

        # Print the thesis
        thesis = result.get("thesis", {})

        print("\n" + "="*70)
        print("INVESTMENT THESIS")
        print("="*70 + "\n")

        print(f"Ticker: {thesis.get('ticker', ticker)}")
        print(f"Company: {thesis.get('company_name', 'N/A')}")
        print(f"Recommendation: {thesis.get('recommendation', 'N/A').upper()}")
        print(f"Conviction: {thesis.get('conviction', 0):.0%}")
        print(f"Target Weight: {thesis.get('target_weight', 0):.1%}")
        print(f"Price Target: {thesis.get('price_target', 'N/A')}")

        print("\n--- THESIS SUMMARY ---")
        print(thesis.get('thesis_summary', 'N/A'))

        print("\n--- BULL CASE ---")
        bull = thesis.get('bull_case', {})
        print(bull.get('summary', 'N/A'))
        for point in bull.get('key_points', []):
            print(f"  • {point}")

        print("\n--- BEAR CASE ---")
        bear = thesis.get('bear_case', {})
        print(bear.get('summary', 'N/A'))
        for point in bear.get('key_points', []):
            print(f"  • {point}")

        print("\n--- KEY RISKS ---")
        for risk in thesis.get('key_risks', []):
            print(f"  ⚠️  {risk}")

        print("\n--- CATALYSTS ---")
        for catalyst in thesis.get('catalysts', []):
            print(f"  🎯 {catalyst}")

        print("\n--- SCORE BREAKDOWN ---")
        scores = thesis.get('score_breakdown', {})
        print(f"  Fundamentals: {scores.get('fundamentals', 'N/A')}/10")
        print(f"  Moat:         {scores.get('moat', 'N/A')}/10")
        print(f"  Sentiment:    {scores.get('sentiment', 'N/A')}/10")
        print(f"  Valuation:    {scores.get('valuation', 'N/A')}/10")
        print(f"  Overall:      {scores.get('overall', 'N/A')}/10")

        print("\n--- FULL THESIS ---")
        print(thesis.get('full_thesis', 'N/A'))

        # Save full result to file
        output_file = f"analysis_{ticker}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✓ Full analysis saved to {output_file}")

    except Exception as e:
        print(f"\n✗ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
