"""
Shrestha Capital - Weekly Scheduled Jobs

Runs every Monday:
- Generate risk reports
- Check for rebalancing needs
- Update performance metrics
"""

import asyncio
from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scheduler.celery_app import app
from database.connection import get_session
from models.fund import Fund
from models.position import Position
from models.risk_report import RiskReport
from models.alert import Alert
from orchestrator.pipelines.risk_pipeline import RiskPipeline
from agents.portfolio.rebalancing_agent import get_rebalancing_agent
from agents.performance.benchmark_tracker_agent import get_benchmark_tracker_agent
from sqlalchemy import select


def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.task(name='scheduler.jobs.weekly.generate_risk_reports')
def generate_risk_reports():
    """
    Generate weekly risk reports for all active funds.
    """
    return run_async(_generate_risk_reports())


async def _generate_risk_reports():
    """Async implementation of risk report generation"""
    print(f"\n[{datetime.now()}] Generating weekly risk reports...")

    risk_pipeline = RiskPipeline()
    reports_generated = 0

    async with get_session() as session:
        # Get all active funds
        stmt = select(Fund).where(Fund.status == "active")
        result = await session.execute(stmt)
        funds = result.scalars().all()

        for fund in funds:
            print(f"  Generating risk report for {fund.name}...")

            try:
                # Get positions
                pos_stmt = select(Position).where(
                    Position.fund_id == fund.id,
                    Position.status == "active"
                )
                pos_result = await session.execute(pos_stmt)
                positions = pos_result.scalars().all()

                if not positions:
                    print(f"    Skipping - no active positions")
                    continue

                # Convert to dict format
                positions_data = [
                    {
                        "ticker": p.ticker,
                        "weight": float(p.target_weight or 0)
                    }
                    for p in positions
                ]

                # Run risk analysis
                report_data = await risk_pipeline.analyze(
                    positions=positions_data,
                    portfolio_value=1000000,  # Default value
                    run_full=True
                )

                # Save risk report
                summary = report_data.get("summary", {})
                var_data = report_data.get("var", {}).get("var_metrics", {})

                risk_report = RiskReport(
                    fund_id=fund.id,
                    report_date=date.today(),
                    var_daily_95=var_data.get("daily_var_95", {}).get("amount", "").replace("$", "").replace(",", "") or None,
                    var_daily_99=var_data.get("daily_var_99", {}).get("amount", "").replace("$", "").replace(",", "") or None,
                    stress_tests=report_data.get("stress_tests"),
                    monte_carlo=report_data.get("monte_carlo"),
                    correlations=report_data.get("correlations"),
                    flags=report_data.get("risk_flags"),
                    recommendations=report_data.get("recommendations"),
                )
                session.add(risk_report)
                reports_generated += 1

                # Create alerts for any risk flags
                flags = report_data.get("risk_flags", [])
                if flags:
                    alert = Alert(
                        fund_id=fund.id,
                        type="risk",
                        title=f"Weekly Risk Report: {len(flags)} flag(s)",
                        message="; ".join(flags[:3]),
                        severity="warning",
                        action_required=False
                    )
                    session.add(alert)

                print(f"    ✓ Risk report generated")

            except Exception as e:
                print(f"    ✗ Error: {str(e)[:100]}")

        await session.commit()

    print(f"\nRisk reports complete. Generated: {reports_generated}")
    return {"status": "complete", "reports_generated": reports_generated}


@app.task(name='scheduler.jobs.weekly.check_rebalancing')
def check_rebalancing():
    """
    Check all funds for rebalancing needs.
    """
    return run_async(_check_rebalancing())


async def _check_rebalancing():
    """Async implementation of rebalancing check"""
    print(f"\n[{datetime.now()}] Checking rebalancing needs...")

    agent = get_rebalancing_agent()
    funds_checked = 0
    rebalance_needed = 0

    async with get_session() as session:
        stmt = select(Fund).where(Fund.status == "active")
        result = await session.execute(stmt)
        funds = result.scalars().all()

        for fund in funds:
            print(f"  Checking {fund.name}...")

            try:
                # Get positions
                pos_stmt = select(Position).where(
                    Position.fund_id == fund.id,
                    Position.status == "active"
                )
                pos_result = await session.execute(pos_stmt)
                positions = pos_result.scalars().all()

                if not positions:
                    continue

                # Convert to format for rebalancing agent
                positions_data = [
                    {
                        "ticker": p.ticker,
                        "target_weight": float(p.target_weight or 0),
                        "current_weight": float(p.current_weight or p.target_weight or 0)
                    }
                    for p in positions
                ]

                # Check rebalancing
                result = await agent.run(
                    task="Check if rebalancing is needed",
                    context={"positions": positions_data}
                )

                funds_checked += 1

                if result.get("needs_rebalancing"):
                    rebalance_needed += 1
                    # Create alert
                    alert = Alert(
                        fund_id=fund.id,
                        type="drift",
                        title="Rebalancing Recommended",
                        message=result.get("summary", "Portfolio drift exceeds threshold"),
                        severity="warning",
                        action_required=True,
                        action_options=["rebalance", "dismiss"]
                    )
                    session.add(alert)
                    print(f"    ⚠️ Rebalancing needed")
                else:
                    print(f"    ✓ No rebalancing needed")

            except Exception as e:
                print(f"    ✗ Error: {str(e)[:50]}")

        await session.commit()

    print(f"\nRebalancing check complete. Needed: {rebalance_needed}/{funds_checked}")
    return {"status": "complete", "funds_checked": funds_checked, "rebalance_needed": rebalance_needed}


@app.task(name='scheduler.jobs.weekly.update_performance')
def update_performance():
    """
    Update weekly performance metrics vs benchmarks.
    """
    return run_async(_update_performance())


async def _update_performance():
    """Async implementation of performance update"""
    print(f"\n[{datetime.now()}] Updating performance metrics...")

    agent = get_benchmark_tracker_agent()
    funds_updated = 0

    async with get_session() as session:
        stmt = select(Fund).where(Fund.status == "active")
        result = await session.execute(stmt)
        funds = result.scalars().all()

        for fund in funds:
            print(f"  Updating {fund.name}...")

            try:
                # Get positions for context
                pos_stmt = select(Position).where(
                    Position.fund_id == fund.id,
                    Position.status == "active"
                )
                pos_result = await session.execute(pos_stmt)
                positions = pos_result.scalars().all()

                positions_data = [
                    {"ticker": p.ticker, "weight": float(p.target_weight or 0)}
                    for p in positions
                ]

                # Get benchmark comparison
                result = await agent.run(
                    task="Compare fund performance to benchmarks",
                    context={
                        "positions": positions_data,
                        "primary_benchmark": fund.benchmark_primary or "QQQ",
                        "secondary_benchmark": fund.benchmark_secondary or "SPY",
                        "fund_return_ytd": 0  # Would need actual tracking
                    }
                )

                funds_updated += 1
                is_outperforming = result.get("benchmark_comparison", {}).get("primary", {}).get("is_outperforming", False)
                print(f"    ✓ {'Outperforming' if is_outperforming else 'Underperforming'} benchmark")

            except Exception as e:
                print(f"    ✗ Error: {str(e)[:50]}")

    print(f"\nPerformance update complete. Updated: {funds_updated}")
    return {"status": "complete", "funds_updated": funds_updated}
