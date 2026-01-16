"""
Analysis endpoints - analyze individual stocks
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestrator.pipelines.analysis_pipeline import analyze_stock
from database.connection import get_db, get_session
from models.thesis import Thesis
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """Request to analyze a stock"""
    ticker: str
    fund_id: Optional[str] = None
    save_thesis: bool = True


class AnalyzeResponse(BaseModel):
    """Response from stock analysis"""
    ticker: str
    recommendation: Optional[str]
    conviction: Optional[float]
    target_weight: Optional[float]
    thesis_summary: Optional[str]
    bull_case: Optional[str]
    bear_case: Optional[str]
    key_risks: Optional[List[str]]
    scores: Optional[dict]
    thesis_id: Optional[str] = None


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_ticker(request: AnalyzeRequest):
    """
    Analyze a stock using the full research pipeline.

    Runs:
    - Fundamentals analysis
    - Moat analysis
    - Sentiment analysis
    - Valuation analysis
    - Thesis synthesis

    Returns a complete investment thesis.
    """
    try:
        # Run analysis pipeline
        result = await analyze_stock(request.ticker.upper())

        thesis_data = result.get("thesis", {})

        # Build response
        response = AnalyzeResponse(
            ticker=request.ticker.upper(),
            recommendation=thesis_data.get("recommendation"),
            conviction=thesis_data.get("conviction"),
            target_weight=thesis_data.get("target_weight"),
            thesis_summary=thesis_data.get("thesis_summary"),
            bull_case=thesis_data.get("bull_case", {}).get("summary") if isinstance(thesis_data.get("bull_case"), dict) else thesis_data.get("bull_case"),
            bear_case=thesis_data.get("bear_case", {}).get("summary") if isinstance(thesis_data.get("bear_case"), dict) else thesis_data.get("bear_case"),
            key_risks=thesis_data.get("key_risks"),
            scores=thesis_data.get("score_breakdown"),
        )

        # Save thesis if requested
        if request.save_thesis:
            async with get_session() as session:
                thesis = Thesis.from_analysis(
                    ticker=request.ticker.upper(),
                    analysis_result=result,
                    fund_id=request.fund_id
                )
                session.add(thesis)
                await session.commit()
                response.thesis_id = thesis.id

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{ticker}")
async def get_analysis(ticker: str):
    """
    Get the latest analysis/thesis for a ticker.
    """
    async with get_session() as session:
        from sqlalchemy import select

        stmt = select(Thesis).where(
            Thesis.ticker == ticker.upper()
        ).order_by(Thesis.created_at.desc()).limit(1)

        result = await session.execute(stmt)
        thesis = result.scalar_one_or_none()

        if not thesis:
            raise HTTPException(status_code=404, detail=f"No analysis found for {ticker}")

        return thesis.to_dict()


class BatchAnalyzeRequest(BaseModel):
    """Request to analyze multiple stocks"""
    tickers: List[str]
    fund_id: Optional[str] = None


@router.post("/analyze/batch")
async def analyze_batch(request: BatchAnalyzeRequest):
    """
    Analyze multiple stocks (runs sequentially to avoid rate limits).
    """
    results = []

    for ticker in request.tickers:
        try:
            result = await analyze_stock(ticker.upper())
            thesis_data = result.get("thesis", {})

            results.append({
                "ticker": ticker.upper(),
                "status": "success",
                "recommendation": thesis_data.get("recommendation"),
                "conviction": thesis_data.get("conviction"),
                "score": thesis_data.get("score_breakdown", {}).get("overall")
            })
        except Exception as e:
            results.append({
                "ticker": ticker.upper(),
                "status": "error",
                "error": str(e)
            })

    return {
        "analyzed": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results
    }
