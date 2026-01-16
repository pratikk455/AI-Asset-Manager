"""
Discovery endpoints - scout and discover stocks
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestrator.pipelines.scout_pipeline import ScoutPipeline

router = APIRouter()


class DiscoverRequest(BaseModel):
    """Request to discover stocks"""
    themes: Optional[List[str]] = None
    mandate: Optional[str] = None
    exclude_tickers: Optional[List[str]] = None
    run_all_scouts: bool = False


class QuickDiscoverRequest(BaseModel):
    """Request for quick themed discovery"""
    theme: str


@router.post("/discover")
async def discover_stocks(request: DiscoverRequest):
    """
    Run the full scout pipeline to discover stocks.

    Runs multiple scouts based on themes:
    - Emerging Leaders Scout
    - Disruption Scout
    - Thematic Scout (for each theme)
    - Smart Money Scout

    Returns a screened universe categorized as HOT/WARM/COLD.
    """
    try:
        pipeline = ScoutPipeline()

        result = await pipeline.discover(
            themes=request.themes,
            mandate=request.mandate,
            exclude_tickers=request.exclude_tickers,
            run_all_scouts=request.run_all_scouts
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discover/theme")
async def discover_theme(request: QuickDiscoverRequest):
    """
    Quick discovery for a single theme.

    Available themes:
    - AI / Machine Learning
    - Fintech / Digital Payments
    - Clean Energy / EVs
    - Cybersecurity
    - Cloud / SaaS
    - Healthcare Innovation
    """
    try:
        pipeline = ScoutPipeline()

        result = await pipeline.quick_discover(request.theme)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discover/themes")
async def list_themes():
    """
    List available themes for discovery.
    """
    return {
        "themes": [
            {
                "id": "ai",
                "name": "AI / Machine Learning",
                "description": "AI infrastructure, applications, and enablers"
            },
            {
                "id": "fintech",
                "name": "Fintech",
                "description": "Digital payments, neobanks, lending platforms"
            },
            {
                "id": "clean_energy",
                "name": "Clean Energy",
                "description": "EVs, solar, wind, energy storage"
            },
            {
                "id": "cybersecurity",
                "name": "Cybersecurity",
                "description": "Endpoint, cloud, and identity security"
            },
            {
                "id": "cloud",
                "name": "Cloud / SaaS",
                "description": "Cloud infrastructure and enterprise software"
            },
            {
                "id": "healthcare",
                "name": "Healthcare Innovation",
                "description": "Telehealth, genomics, medical devices"
            },
            {
                "id": "future_of_work",
                "name": "Future of Work",
                "description": "Collaboration, HR tech, learning platforms"
            },
            {
                "id": "consumer_tech",
                "name": "Consumer Tech",
                "description": "E-commerce, streaming, gaming"
            }
        ]
    }
