"""
Shrestha Capital - Daily Scheduled Jobs

Runs every market day:
- Monitor positions for news/events
- Update prices after market close
- Create alerts for material events
"""

import asyncio
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scheduler.celery_app import app
from database.connection import get_session
from models.fund import Fund
from models.position import Position
from models.alert import Alert
from agents.portfolio.position_monitor_agent import get_position_monitor_agent
from llm.gemini_client import get_gemini_client
from sqlalchemy import select


def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.task(name='scheduler.jobs.daily.monitor_all_positions')
def monitor_all_positions():
    """
    Monitor all active positions for news and events.
    Creates alerts for material findings.
    """
    return run_async(_monitor_all_positions())


async def _monitor_all_positions():
    """Async implementation of position monitoring"""
    print(f"\n[{datetime.now()}] Starting daily position monitoring...")

    agent = get_position_monitor_agent()
    alerts_created = 0

    async with get_session() as session:
        # Get all active funds
        stmt = select(Fund).where(Fund.status == "active")
        result = await session.execute(stmt)
        funds = result.scalars().all()

        for fund in funds:
            print(f"  Monitoring {fund.name}...")

            # Get fund positions
            pos_stmt = select(Position).where(
                Position.fund_id == fund.id,
                Position.status == "active"
            )
            pos_result = await session.execute(pos_stmt)
            positions = pos_result.scalars().all()

            for position in positions:
                try:
                    # Monitor this position
                    result = await agent.run(
                        task="Check for material news and events",
                        context={
                            "ticker": position.ticker,
                            "weight": float(position.target_weight or 0),
                        }
                    )

                    # Create alert if needed
                    alert_level = result.get("alert_level", "info")
                    if alert_level in ["warning", "critical"]:
                        alert = Alert(
                            fund_id=fund.id,
                            type="news",
                            ticker=position.ticker,
                            title=f"{position.ticker}: {result.get('summary', 'Material event detected')[:100]}",
                            message=result.get("summary", ""),
                            severity=alert_level,
                            action_required=alert_level == "critical",
                            action_options=["hold", "review", "trim", "sell"] if alert_level == "critical" else None
                        )
                        session.add(alert)
                        alerts_created += 1
                        print(f"    ⚠️ Alert created for {position.ticker}")
                    else:
                        print(f"    ✓ {position.ticker}: No material events")

                except Exception as e:
                    print(f"    ✗ Error monitoring {position.ticker}: {str(e)[:50]}")

        await session.commit()

    print(f"\nMonitoring complete. Alerts created: {alerts_created}")
    return {"status": "complete", "alerts_created": alerts_created}


@app.task(name='scheduler.jobs.daily.update_all_prices')
def update_all_prices():
    """
    Update prices for all positions after market close.
    """
    return run_async(_update_all_prices())


async def _update_all_prices():
    """Async implementation of price updates"""
    print(f"\n[{datetime.now()}] Starting daily price update...")

    client = get_gemini_client()
    updated = 0

    async with get_session() as session:
        # Get all unique tickers from active positions
        stmt = select(Position).where(Position.status == "active")
        result = await session.execute(stmt)
        positions = result.scalars().all()

        # Get unique tickers
        tickers = list(set(p.ticker for p in positions))
        print(f"  Updating prices for {len(tickers)} tickers...")

        for ticker in tickers:
            try:
                # Get current price via Gemini search
                response = await client.search(
                    f"What is the current stock price of {ticker}? Just give me the price number."
                )

                # Parse price from response
                price_str = response.get("text", "")
                # Simple price extraction
                import re
                match = re.search(r'\$?([\d,]+\.?\d*)', price_str)
                if match:
                    price = float(match.group(1).replace(",", ""))

                    # Update all positions with this ticker
                    for pos in positions:
                        if pos.ticker == ticker:
                            pos.current_price = price
                            # Calculate P&L if we have cost basis
                            if pos.cost_basis:
                                pos.unrealized_pnl_pct = (price - float(pos.cost_basis)) / float(pos.cost_basis)

                    updated += 1
                    print(f"    ✓ {ticker}: ${price:.2f}")

            except Exception as e:
                print(f"    ✗ Error updating {ticker}: {str(e)[:50]}")

        await session.commit()

    print(f"\nPrice update complete. Updated: {updated}/{len(tickers)}")
    return {"status": "complete", "updated": updated}
