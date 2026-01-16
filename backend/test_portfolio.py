"""
Test the portfolio construction flow:
1. Analyze multiple stocks
2. Build portfolio from theses
3. Run risk analysis on portfolio
"""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from orchestrator.pipelines.analysis_pipeline import analyze_stock
from agents.portfolio.pm_agent import get_pm_agent
from orchestrator.pipelines.risk_pipeline import RiskPipeline


async def main():
    print("\n" + "="*70)
    print("SHRESTHA CAPITAL - Portfolio Construction Test")
    print("="*70 + "\n")

    # Step 1: Analyze a few stocks
    tickers = ["NVDA", "GOOGL", "AMZN"]

    print("STEP 1: Analyze stocks for theses\n")

    theses = []
    for ticker in tickers:
        print(f"  Analyzing {ticker}...")
        try:
            result = await analyze_stock(ticker)
            thesis_data = result.get("thesis", {})

            theses.append({
                "ticker": ticker,
                "recommendation": thesis_data.get("recommendation", "hold"),
                "conviction": thesis_data.get("conviction", 0.5),
                "thesis_summary": thesis_data.get("thesis_summary", ""),
                "target_weight": thesis_data.get("target_weight", 0.05)
            })
            print(f"  ✓ {ticker}: {thesis_data.get('recommendation', 'N/A')} ({thesis_data.get('conviction', 0):.0%})")
        except Exception as e:
            print(f"  ✗ {ticker} failed: {str(e)[:50]}")

    if not theses:
        print("No theses generated. Exiting.")
        return

    # Step 2: Build portfolio
    print(f"\n{'='*70}")
    print("STEP 2: Construct Portfolio")
    print("="*70 + "\n")

    pm = get_pm_agent()

    portfolio = await pm.run(
        task="Construct an optimal growth portfolio from these theses",
        context={
            "theses": theses,
            "mandate": "US Large Cap Growth",
            "constraints": {
                "max_position_size": 0.12,
                "min_positions": 3,
                "cash_target": 0.05
            }
        }
    )

    print("\nPORTFOLIO CONSTRUCTED:")
    positions = portfolio.get("positions", [])
    for pos in positions:
        print(f"  {pos.get('ticker')}: {pos.get('weight', 0):.1%} - {pos.get('thesis_summary', '')[:40]}...")

    print(f"\n  Total positions: {portfolio.get('portfolio_summary', {}).get('total_positions', 'N/A')}")
    print(f"  Cash: {portfolio.get('portfolio_summary', {}).get('cash_weight', 0):.1%}")

    # Step 3: Run risk analysis
    print(f"\n{'='*70}")
    print("STEP 3: Risk Analysis")
    print("="*70 + "\n")

    risk_positions = [
        {"ticker": p.get("ticker"), "weight": p.get("weight", 0.05)}
        for p in positions
    ]

    risk_pipeline = RiskPipeline()
    risk_report = await risk_pipeline.analyze(
        positions=risk_positions,
        portfolio_value=1000000,
        run_full=False  # Just stress test and VaR for speed
    )

    print("\nRISK SUMMARY:")
    summary = risk_report.get("summary", {})
    print(f"  Worst case drawdown: {summary.get('worst_case_drawdown', 'N/A')}")
    print(f"  Daily VaR (95%): {summary.get('daily_var_95', 'N/A')}")
    print(f"  Risk level: {summary.get('overall_risk_level', 'N/A')}")

    if risk_report.get("risk_flags"):
        print("\n  Risk Flags:")
        for flag in risk_report["risk_flags"]:
            print(f"    ⚠️  {flag}")

    # Save results
    output = {
        "theses": theses,
        "portfolio": portfolio,
        "risk_report": risk_report
    }

    with open("portfolio_test_result.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'='*70}")
    print("PORTFOLIO CONSTRUCTION COMPLETE!")
    print(f"{'='*70}\n")

    print("✓ Results saved to portfolio_test_result.json")


if __name__ == "__main__":
    asyncio.run(main())
