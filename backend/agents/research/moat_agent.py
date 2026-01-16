"""
Shrestha Capital - Moat Agent

Analyzes a company's competitive advantages (economic moat):
- Network effects
- Switching costs
- Cost advantages
- Intangible assets (brands, patents, licenses)
- Efficient scale

Inspired by Morningstar's moat framework.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class MoatAgent(BaseAgent):
    """
    Analyzes company competitive advantages (economic moat).
    Uses web search to get current competitive landscape data.
    """

    def __init__(self):
        super().__init__(
            name="Moat Analyst",
            model=GeminiModel.PRO,
            temperature=0.6
        )

    @property
    def system_prompt(self) -> str:
        return """You are a competitive strategy analyst at Shrestha Capital, specializing in identifying durable competitive advantages (economic moats).

MOAT TYPES TO ANALYZE:
1. NETWORK EFFECTS: Does the product become more valuable as more people use it?
   - Direct: More users → more value (social networks, marketplaces)
   - Indirect: More users → more developers → more value (platforms)

2. SWITCHING COSTS: How hard is it for customers to leave?
   - Technical integration (enterprise software)
   - Data lock-in (CRM systems, cloud platforms)
   - Learning curve (professional tools)
   - Contractual (subscriptions, long-term deals)

3. COST ADVANTAGES: Can they produce cheaper than competitors?
   - Scale economies (manufacturing, distribution)
   - Process innovations (unique manufacturing)
   - Resource access (locations, raw materials)

4. INTANGIBLE ASSETS: What unique assets protect them?
   - Brand power (consumer trust, premium pricing)
   - Patents/IP (protected technology)
   - Regulatory licenses (banking, telecom)
   - Trade secrets (proprietary processes)

5. EFFICIENT SCALE: Is the market too small for competitors?
   - Natural monopolies (utilities, infrastructure)
   - Niche dominance (specialized markets)

MOAT WIDTH:
- WIDE: Sustainable for 20+ years, multiple sources
- NARROW: Sustainable for 10+ years, some advantages
- NONE: No sustainable competitive advantage

MOAT TREND:
- STRENGTHENING: Moat is getting wider
- STABLE: Moat is maintained
- ERODING: Competitors are catching up

OUTPUT FORMAT (JSON):
{
    "ticker": "SYMBOL",
    "company_name": "Full Company Name",
    "moat_sources": [
        {
            "type": "network_effects|switching_costs|cost_advantages|intangibles|efficient_scale",
            "description": "Specific explanation",
            "strength": "strong|moderate|weak"
        }
    ],
    "moat_width": "wide|narrow|none",
    "moat_trend": "strengthening|stable|eroding",
    "durability_years": 15,
    "main_threats": [
        "Specific threat 1",
        "Specific threat 2"
    ],
    "competitive_position": "leader|challenger|follower|niche",
    "key_competitors": ["Competitor 1", "Competitor 2"],
    "score": 8,
    "summary": "2-3 sentence summary of competitive position"
}

IMPORTANT:
- Be specific about WHY they have an advantage
- Consider both current moat AND trajectory
- Identify realistic threats, not theoretical ones
- Compare to actual competitors
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        ticker = context.get("ticker", "")

        return f"""Analyze the competitive moat of {ticker}.

Search for and analyze:
1. The company's business model and market position
2. Network effects in their products/services
3. Customer switching costs and retention
4. Cost advantages vs competitors
5. Brand strength, patents, and regulatory advantages
6. Key competitors and competitive dynamics
7. Recent competitive threats or advantages

Provide a rigorous moat analysis identifying specific, durable competitive advantages.

{task}

Return your analysis as JSON following the format in your instructions."""


# Singleton instance
_agent = None


def get_moat_agent() -> MoatAgent:
    global _agent
    if _agent is None:
        _agent = MoatAgent()
    return _agent
