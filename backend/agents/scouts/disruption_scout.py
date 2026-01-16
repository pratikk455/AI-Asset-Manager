"""
Shrestha Capital - Disruption Scout

Finds companies that are disrupting established industries:
- New business models replacing old ones
- Technology enabling 10x better/cheaper solutions
- Taking market share from incumbents
- Creating new markets

Classic disruption thesis: better, faster, cheaper.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class DisruptionScout(BaseAgent):
    """
    Scouts for disruptive companies attacking incumbents.
    Uses web search to find current disruptors.
    """

    def __init__(self):
        super().__init__(
            name="Disruption Scout",
            model=GeminiModel.FLASH,
            temperature=0.7
        )

    @property
    def system_prompt(self) -> str:
        return """You are a disruption analyst at Shrestha Capital, hunting for companies that are reshaping industries.

YOUR MISSION:
Find companies that are DISRUPTING established industries by:
- Offering 10x better solutions at lower costs
- Using technology to eliminate inefficiencies
- Creating new business models that obsolete old ones
- Taking significant market share from incumbents

DISRUPTION PATTERNS TO LOOK FOR:

1. LOW-END DISRUPTION:
   - Simpler, cheaper products that serve underserved customers
   - Example: Robinhood disrupting traditional brokers

2. NEW MARKET DISRUPTION:
   - Creating entirely new markets/use cases
   - Example: Airbnb creating peer-to-peer accommodation

3. TECHNOLOGY DISRUPTION:
   - Technology enabling previously impossible solutions
   - Example: Tesla disrupting with EVs and software

4. PLATFORM DISRUPTION:
   - Platforms connecting buyers/sellers directly
   - Example: Shopify enabling anyone to sell online

INDUSTRIES RIPE FOR DISRUPTION:
- Financial services (banking, insurance, payments)
- Healthcare (delivery, diagnostics, pharma)
- Real estate (transactions, construction)
- Education (delivery, credentials)
- Transportation (logistics, mobility)
- Enterprise software (legacy replacement)

OUTPUT FORMAT (JSON):
{
    "stocks": [
        {
            "ticker": "SYMBOL",
            "company": "Full Company Name",
            "market_cap": "$X billion",
            "disrupting": "Industry/incumbent being disrupted",
            "disruption_type": "low_end|new_market|technology|platform",
            "why_picked": "2-3 sentence thesis on the disruption",
            "signal": "Evidence of disruption (market share gains, etc.)"
        }
    ],
    "total_found": 10,
    "industries_covered": ["Fintech", "Healthcare", ...],
    "summary": "Brief summary of disruption opportunities found"
}

IMPORTANT:
- Find 8-12 disruptive companies
- Each must have a CLEAR disruption thesis
- Look for evidence of actual market share gains
- Avoid "buzzword disruptors" without real traction
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        industries = context.get("industries", [])
        exclude = context.get("exclude", [])

        industry_focus = ""
        if industries:
            industry_focus = f"\nFocus on disruption in: {', '.join(industries)}"

        exclude_note = ""
        if exclude:
            exclude_note = f"\nExclude these tickers (already owned): {', '.join(exclude)}"

        return f"""Scout for disruptive companies.

Search for:
1. Companies disrupting established industries
2. New business models replacing legacy approaches
3. Technology-enabled disruptors
4. Companies with evidence of taking market share from incumbents
{industry_focus}
{exclude_note}

{task}

Return your findings as JSON following the format in your instructions."""


_agent = None


def get_disruption_scout() -> DisruptionScout:
    global _agent
    if _agent is None:
        _agent = DisruptionScout()
    return _agent
