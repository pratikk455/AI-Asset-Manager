"""
Chat endpoints - conversational interface for fund creation and management
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from models.conversation import Conversation
from models.fund import Fund
from models.position import Position
from agents.conversation.intent_interpreter_agent import get_intent_interpreter_agent
from orchestrator.pipelines.scout_pipeline import ScoutPipeline
from orchestrator.pipelines.analysis_pipeline import analyze_stock
from agents.portfolio.pm_agent import get_pm_agent
from sqlalchemy import select

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message from user"""
    message: str
    conversation_id: Optional[str] = None
    fund_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response to chat message"""
    message: str
    conversation_id: str
    intent: Optional[str] = None
    data: Optional[Dict] = None
    actions: Optional[List[str]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """
    Send a chat message and get a response.

    This is the main conversational interface for:
    - Creating funds
    - Modifying portfolios
    - Querying performance
    - Getting insights
    """
    try:
        async with get_session() as session:
            # Load or create conversation
            conversation = None
            if request.conversation_id:
                stmt = select(Conversation).where(Conversation.id == request.conversation_id)
                result = await session.execute(stmt)
                conversation = result.scalar_one_or_none()

            if not conversation:
                conversation = Conversation(
                    fund_id=request.fund_id,
                    phase="creation" if not request.fund_id else "management",
                    messages=[]
                )
                session.add(conversation)
                await session.flush()

            # Add user message
            conversation.add_message("user", request.message)

            # Parse intent
            intent_agent = get_intent_interpreter_agent()
            intent = await intent_agent.run(
                task="Parse this user message",
                context={
                    "message": request.message,
                    "history": conversation.messages or [],
                    "current_fund": None
                }
            )

            intent_type = intent.get("intent", "unclear").lower()  # Normalize to lowercase
            response_text = intent.get("suggested_response", "I understand. Let me help you with that.")

            # Handle different intents
            data = None
            actions = None

            if intent_type == "create_fund":
                # Extract fund parameters
                fund_params = intent.get("fund_params", {})
                themes = fund_params.get("themes", [])
                specific_stocks = fund_params.get("specific_stocks", [])
                fund_name = fund_params.get("name", f"{''.join(t.title() for t in themes[:2])} Fund" if themes else "New Growth Fund")

                # Create the fund in the database
                import re
                slug = re.sub(r'[^a-z0-9]+', '-', fund_name.lower()).strip('-')

                new_fund = Fund(
                    name=fund_name,
                    slug=slug,
                    category=fund_params.get("category", "growth"),
                    mandate=fund_params.get("mandate"),
                    status="building"
                )
                session.add(new_fund)
                await session.flush()

                # Link conversation to fund
                conversation.fund_id = new_fund.id

                response_text = f"Creating **{fund_name}**! "
                if themes:
                    response_text += f"Focused on {', '.join(themes)}. "
                if specific_stocks:
                    response_text += f"Including {', '.join(specific_stocks)}. "
                response_text += "Now scouting for opportunities..."

                # Store state for next steps
                conversation.state = {
                    "phase": "scouting",
                    "fund_params": fund_params,
                    "fund_id": new_fund.id
                }
                actions = ["scouting", "analyzing", "building_portfolio"]
                data = {"fund_id": new_fund.id, "fund_name": fund_name}

            elif intent_type == "query_performance":
                response_text = "Let me check the fund's performance for you."
                actions = ["fetch_performance"]

            elif intent_type == "query_risk":
                response_text = "I'll run a risk analysis on your portfolio."
                actions = ["run_risk_analysis"]

            elif intent_type == "command_trade":
                trade = intent.get("trade_params", {})
                ticker = trade.get("ticker", "")
                action = trade.get("action", "")
                response_text = f"You want to {action} {ticker}. Let me confirm: Should I proceed with this trade?"
                actions = ["confirm_trade"]
                data = {"trade": trade}

            elif intent_type == "unclear":
                response_text = intent.get("clarification_needed") or "Could you tell me more about what you'd like to do? I can help you create funds, analyze stocks, or manage your portfolio."

            else:
                response_text = intent.get("suggested_response", "I'm processing your request...")

            # Add assistant response
            conversation.add_message("assistant", response_text)
            await session.commit()

            return ChatResponse(
                message=response_text,
                conversation_id=conversation.id,
                intent=intent_type,
                data=data,
                actions=actions
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/execute")
async def execute_action(
    conversation_id: str,
    action: str
):
    """
    Execute an action from a chat conversation.

    Actions:
    - scouting: Run scouts to discover stocks
    - analyzing: Analyze discovered stocks
    - building_portfolio: Build portfolio from theses
    - confirm_trade: Confirm a trade
    """
    try:
        async with get_session() as session:
            # Load conversation
            stmt = select(Conversation).where(Conversation.id == conversation_id)
            result = await session.execute(stmt)
            conversation = result.scalar_one_or_none()

            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            state = conversation.state or {}
            fund_params = state.get("fund_params", {})

            if action == "scouting":
                # Run scout pipeline
                themes = fund_params.get("themes", ["growth"])
                pipeline = ScoutPipeline()

                discovery = await pipeline.discover(
                    themes=themes,
                    mandate=fund_params.get("mandate", ""),
                    exclude_tickers=fund_params.get("exclude", [])
                )

                # Get hot stocks
                hot_stocks = discovery.get("universe", {}).get("hot", [])
                hot_tickers = [s.get("ticker") for s in hot_stocks[:10]]

                state["discovered_stocks"] = hot_tickers
                state["phase"] = "discovered"
                conversation.state = state

                await session.commit()

                return {
                    "status": "complete",
                    "message": f"Found {len(hot_tickers)} promising stocks to analyze.",
                    "stocks": hot_tickers
                }

            elif action == "analyzing":
                # Analyze discovered stocks
                tickers = state.get("discovered_stocks", [])[:5]  # Analyze top 5

                theses = []
                for ticker in tickers:
                    try:
                        result = await analyze_stock(ticker)
                        thesis = result.get("thesis", {})
                        theses.append({
                            "ticker": ticker,
                            "recommendation": thesis.get("recommendation"),
                            "conviction": thesis.get("conviction"),
                            "thesis_summary": thesis.get("thesis_summary")
                        })
                    except:
                        pass

                state["theses"] = theses
                state["phase"] = "analyzed"
                conversation.state = state

                await session.commit()

                return {
                    "status": "complete",
                    "message": f"Analyzed {len(theses)} stocks.",
                    "theses": theses
                }

            elif action == "building_portfolio":
                # Build portfolio
                theses = state.get("theses", [])
                fund_id = state.get("fund_id")

                pm = get_pm_agent()
                portfolio = await pm.run(
                    task="Build optimal portfolio",
                    context={
                        "theses": theses,
                        "mandate": fund_params.get("mandate", ""),
                        "constraints": fund_params.get("constraints", {})
                    }
                )

                # Add positions to the fund
                positions_created = []
                if fund_id and portfolio:
                    # PM agent may return "positions" or "allocations"
                    allocations = portfolio.get("positions", portfolio.get("allocations", []))
                    for alloc in allocations:
                        ticker = alloc.get("ticker")
                        if ticker:
                            position = Position(
                                fund_id=fund_id,
                                ticker=ticker,
                                company_name=alloc.get("company", alloc.get("company_name", ticker)),
                                target_weight=alloc.get("weight", 0.05),
                                current_weight=alloc.get("weight", 0.05),
                                status="proposed"
                            )
                            session.add(position)
                            positions_created.append(ticker)

                    # Update fund status
                    stmt = select(Fund).where(Fund.id == fund_id)
                    result = await session.execute(stmt)
                    fund = result.scalar_one_or_none()
                    if fund:
                        fund.status = "active"

                state["proposed_portfolio"] = portfolio
                state["phase"] = "complete"
                conversation.state = state

                await session.commit()

                return {
                    "status": "complete",
                    "message": f"Portfolio built with {len(positions_created)} positions! Your fund is now active.",
                    "portfolio": portfolio,
                    "fund_id": fund_id,
                    "positions": positions_created
                }

            else:
                return {"status": "unknown_action", "action": action}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    async with get_session() as session:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(stmt)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return conversation.to_dict()
