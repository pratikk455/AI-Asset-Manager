"""
Fund endpoints - CRUD for funds
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from models.fund import Fund
from models.position import Position
from models.thesis import Thesis
from sqlalchemy import select

router = APIRouter()


class CreateFundRequest(BaseModel):
    """Request to create a fund"""
    name: str
    mandate: Optional[str] = None
    category: Optional[str] = None
    benchmark_primary: Optional[str] = None
    benchmark_secondary: Optional[str] = None
    peer_funds: Optional[List[str]] = None
    config: Optional[dict] = None


class AddPositionRequest(BaseModel):
    """Request to add a position to a fund"""
    ticker: str
    target_weight: float
    thesis_id: Optional[str] = None


class FundResponse(BaseModel):
    """Fund response"""
    id: str
    name: str
    mandate: Optional[str]
    category: Optional[str]
    status: str
    benchmark_primary: Optional[str]
    positions_count: int = 0


@router.post("/funds", response_model=FundResponse)
async def create_fund(request: CreateFundRequest):
    """
    Create a new fund.
    """
    async with get_session() as session:
        # Create slug from name
        slug = request.name.lower().replace(" ", "-")

        fund = Fund(
            name=request.name,
            slug=slug,
            mandate=request.mandate,
            category=request.category,
            benchmark_primary=request.benchmark_primary,
            benchmark_secondary=request.benchmark_secondary,
            peer_funds=request.peer_funds,
            config=request.config,
            status="draft"
        )

        session.add(fund)
        await session.commit()
        await session.refresh(fund)

        return FundResponse(
            id=fund.id,
            name=fund.name,
            mandate=fund.mandate,
            category=fund.category,
            status=fund.status,
            benchmark_primary=fund.benchmark_primary,
            positions_count=0
        )


@router.get("/funds")
async def list_funds():
    """
    List all funds.
    """
    async with get_session() as session:
        stmt = select(Fund).order_by(Fund.created_at.desc())
        result = await session.execute(stmt)
        funds = result.scalars().all()

        return {
            "funds": [f.to_dict() for f in funds],
            "total": len(funds)
        }


@router.get("/funds/{fund_id}")
async def get_fund(fund_id: str):
    """
    Get fund details with positions.
    """
    async with get_session() as session:
        stmt = select(Fund).where(Fund.id == fund_id)
        result = await session.execute(stmt)
        fund = result.scalar_one_or_none()

        if not fund:
            raise HTTPException(status_code=404, detail="Fund not found")

        # Get positions
        pos_stmt = select(Position).where(Position.fund_id == fund_id)
        pos_result = await session.execute(pos_stmt)
        positions = pos_result.scalars().all()

        return {
            **fund.to_dict(),
            "positions": [p.to_dict() for p in positions],
            "positions_count": len(positions)
        }


@router.post("/funds/{fund_id}/positions")
async def add_position(fund_id: str, request: AddPositionRequest):
    """
    Add a position to a fund.
    """
    async with get_session() as session:
        # Verify fund exists
        stmt = select(Fund).where(Fund.id == fund_id)
        result = await session.execute(stmt)
        fund = result.scalar_one_or_none()

        if not fund:
            raise HTTPException(status_code=404, detail="Fund not found")

        # Check if position already exists
        pos_stmt = select(Position).where(
            Position.fund_id == fund_id,
            Position.ticker == request.ticker.upper()
        )
        pos_result = await session.execute(pos_stmt)
        existing = pos_result.scalar_one_or_none()

        if existing:
            # Update existing position
            existing.target_weight = request.target_weight
            if request.thesis_id:
                existing.thesis_id = request.thesis_id
            await session.commit()
            return existing.to_dict()

        # Create new position
        position = Position(
            fund_id=fund_id,
            ticker=request.ticker.upper(),
            target_weight=request.target_weight,
            thesis_id=request.thesis_id,
            status="active"
        )

        session.add(position)
        await session.commit()
        await session.refresh(position)

        return position.to_dict()


@router.delete("/funds/{fund_id}/positions/{ticker}")
async def remove_position(fund_id: str, ticker: str):
    """
    Remove a position from a fund.
    """
    async with get_session() as session:
        stmt = select(Position).where(
            Position.fund_id == fund_id,
            Position.ticker == ticker.upper()
        )
        result = await session.execute(stmt)
        position = result.scalar_one_or_none()

        if not position:
            raise HTTPException(status_code=404, detail="Position not found")

        await session.delete(position)
        await session.commit()

        return {"status": "deleted", "ticker": ticker.upper()}


@router.post("/funds/{fund_id}/activate")
async def activate_fund(fund_id: str):
    """
    Activate a fund (move from draft to active).
    """
    async with get_session() as session:
        stmt = select(Fund).where(Fund.id == fund_id)
        result = await session.execute(stmt)
        fund = result.scalar_one_or_none()

        if not fund:
            raise HTTPException(status_code=404, detail="Fund not found")

        fund.status = "active"
        fund.inception_date = date.today()
        await session.commit()

        return {"status": "activated", "fund_id": fund_id}
