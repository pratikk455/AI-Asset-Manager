"""
Shrestha Capital - Intent Interpreter Agent

Parses user's natural language into structured intents:
- Create fund requests
- Modify fund requests
- Query requests (performance, risk, etc.)
- Command requests (rebalance, sell, etc.)

This is the "front door" for user interaction.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class IntentInterpreterAgent(BaseAgent):
    """
    Interprets user intent from natural language.
    Uses Flash model for speed.
    """

    def __init__(self):
        super().__init__(
            name="Intent Interpreter",
            model=GeminiModel.FLASH,
            temperature=0.3
        )

    @property
    def system_prompt(self) -> str:
        return """You are an intent parser for Shrestha Capital, an AI-powered asset management system.

YOUR MISSION:
Parse the user's natural language request into a structured intent. BE DECISIVE - don't ask for clarification unless absolutely necessary. The user trusts the AI to make smart decisions.

CRITICAL RULES:
1. BIAS TOWARDS ACTION - When the user says "go for it", "do it", "make it", "yes", "proceed", "let's go", "sounds good", "you decide" - EXECUTE, don't ask more questions
2. USE SMART DEFAULTS - If user doesn't specify number of positions, default to 15. If no risk level, default to moderate.
3. INFER FROM CONTEXT - Look at conversation history to understand what user wants
4. NEVER ask "what kind of fund" if user already described it in prior messages
5. When user says "no" to a clarifying question, it means "I don't have preferences, you decide"

INTENT TYPES:

1. CREATE_FUND:
   User wants to create a new fund. Trigger this when user describes ANY investment theme or strategy.
   Examples:
   - "I want to create a fintech fund"
   - "Make me an AI-focused portfolio"
   - "tech fund"
   - "futuristic companies"
   - "best stocks for 2025"
   - "go for it" (after discussing a fund idea)
   - "make the fund"
   - "yes" or "do it" (in context of fund creation)

2. MODIFY_FUND:
   User wants to change an existing fund
   Examples: "Add NVDA to my fund", "Remove PYPL", "Increase TSLA to 10%"

3. QUERY_PERFORMANCE:
   User asks about performance
   Examples: "How's my fund doing?", "What's my YTD return?"

4. QUERY_RISK:
   User asks about risk
   Examples: "What if there's a crash?", "How risky is my portfolio?"

5. QUERY_POSITION:
   User asks about a specific position
   Examples: "Tell me about NVDA", "Why do we own GOOGL?"

6. COMMAND_REBALANCE:
   User wants to rebalance
   Examples: "Rebalance my portfolio", "Check drift"

7. COMMAND_TRADE:
   User wants to trade
   Examples: "Sell COIN", "Buy more NVDA", "Trim TSLA to 5%"

8. QUERY_GENERAL:
   General questions
   Examples: "What stocks should I look at?", "What's your view on AI?"

9. UNCLEAR:
   ONLY use this if there's genuinely no context at all. Check conversation history first!

OUTPUT FORMAT (JSON):
{
    "intent": "create_fund|modify_fund|query_performance|query_risk|query_position|command_rebalance|command_trade|query_general|unclear",
    "confidence": 0.95,
    "fund_params": {
        "name": "Fund name or generate one based on theme",
        "mandate": "Investment mandate/strategy - infer from conversation",
        "themes": ["theme1", "theme2"],
        "risk_level": "conservative|moderate|aggressive",
        "num_positions": 15,
        "constraints": {
            "max_position_size": 0.10,
            "sectors_to_avoid": []
        },
        "specific_stocks": []
    },
    "clarification_needed": null,
    "parsed_request": "One sentence summary of what user wants",
    "suggested_response": "Acknowledgment that you're starting the work, NOT a question"
}

SMART DEFAULTS:
- num_positions: 15 (if not specified)
- risk_level: "moderate" (if not specified, but use "aggressive" for growth/tech themes)
- max_position_size: 0.10 (10%)
- If user says "futuristic tech" or similar → themes: ["AI", "tech", "innovation", "disruptive technology"]
- If user mentions "like NVDA/TSLA in 2015" → themes: ["high-growth", "emerging tech leaders", "disruptive innovation"]

EXTRACTION TIPS:
- "Aggressive" → risk_level: aggressive
- "About 15-20 stocks" → num_positions: 17
- "Must include X" → specific_stocks: [X]
- "No banks" → constraints.sectors_to_avoid: ["Financials"]
- "Small to mid cap" → constraints.market_cap_range: "small-mid"
- "stable + research" → mix of large-cap leaders AND high-growth emerging companies

IMPORTANT:
- TAKE ACTION, don't ask questions
- Use conversation history to fill in details
- Generate a fund name if user doesn't provide one
- suggested_response should confirm action, e.g. "I'll create your Futuristic Tech Fund now. Scouting for high-growth opportunities..."
- NEVER output "Could you please clarify" - make smart assumptions instead"""

    @property
    def needs_search(self) -> bool:
        return False

    def _build_prompt(self, task: str, context: dict) -> str:
        message = context.get("message", "")
        conversation_history = context.get("history", [])
        current_fund = context.get("current_fund", None)

        history_str = ""
        if conversation_history:
            history_str = "\n=== CONVERSATION HISTORY (USE THIS FOR CONTEXT) ===\n"
            for msg in conversation_history[-10:]:  # Last 10 messages for more context
                history_str += f"{msg['role']}: {msg['content']}\n"
            history_str += "=== END HISTORY ===\n"

        fund_context = ""
        if current_fund:
            fund_context = f"\n=== CURRENT FUND CONTEXT ===\nFund: {current_fund.get('name', 'Unknown')}\n"

        return f"""Parse the user's intent from this message. USE THE CONVERSATION HISTORY to understand context.
{history_str}
{fund_context}
=== CURRENT USER MESSAGE ===
{message}

{task}

REMEMBER: Be decisive. If user has been discussing creating a fund, and now says something like "go for it" or "make it" or "yes", the intent is CREATE_FUND.

Return the parsed intent as JSON following the format in your instructions."""


_agent = None


def get_intent_interpreter_agent() -> IntentInterpreterAgent:
    global _agent
    if _agent is None:
        _agent = IntentInterpreterAgent()
    return _agent
