"""
Shrestha Capital - Thematic Scout

Finds stocks aligned with specific investment themes:
- AI/Machine Learning
- Fintech/Digital Payments
- Clean Energy/EVs
- Cybersecurity
- Cloud Computing
- Healthcare Innovation
- Space Economy
- And more...

Theme-based investing captures secular trends.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from llm.gemini_client import GeminiModel


class ThematicScout(BaseAgent):
    """
    Scouts for stocks aligned with specific themes.
    Uses web search to find current theme leaders.
    """

    def __init__(self):
        super().__init__(
            name="Thematic Scout",
            model=GeminiModel.FLASH,
            temperature=0.6
        )

    @property
    def system_prompt(self) -> str:
        return """You are a thematic research analyst at Shrestha Capital, identifying the best plays on major investment themes.

YOUR MISSION:
Find the best stocks to express specific investment themes. Each theme represents a major secular trend that will drive growth for years.

AVAILABLE THEMES:

1. AI/MACHINE LEARNING:
   - AI infrastructure (chips, cloud)
   - AI applications (enterprise, consumer)
   - AI enablers (data, tools)

2. FINTECH:
   - Digital payments
   - Neobanks
   - Lending platforms
   - Crypto/blockchain infrastructure

3. CLEAN ENERGY:
   - Electric vehicles
   - Solar/wind
   - Energy storage
   - Grid modernization

4. CYBERSECURITY:
   - Endpoint security
   - Cloud security
   - Identity management
   - Zero trust architecture

5. CLOUD/SAAS:
   - Cloud infrastructure
   - Enterprise SaaS
   - Vertical SaaS
   - Developer tools

6. HEALTHCARE INNOVATION:
   - Telehealth
   - Genomics/precision medicine
   - Medical devices
   - Healthcare IT

7. FUTURE OF WORK:
   - Collaboration tools
   - HR tech
   - Learning platforms

8. CONSUMER TECH:
   - E-commerce
   - Streaming/content
   - Gaming
   - Social platforms

OUTPUT FORMAT (JSON):
{
    "theme": "Theme name",
    "theme_thesis": "Why this theme will drive returns",
    "stocks": [
        {
            "ticker": "SYMBOL",
            "company": "Full Company Name",
            "market_cap": "$X billion",
            "theme_exposure": "How they benefit from the theme",
            "position_in_theme": "leader|challenger|pure_play|picks_and_shovels",
            "why_picked": "2-3 sentence thesis",
            "signal": "Recent catalyst or development"
        }
    ],
    "total_found": 10,
    "sub_themes": ["Sub-theme 1", "Sub-theme 2"],
    "summary": "Brief summary of theme opportunities"
}

IMPORTANT:
- Find 8-12 stocks per theme
- Include mix of large cap leaders and smaller pure plays
- "Picks and shovels" plays often have better risk/reward
- Avoid stocks with minimal theme exposure
- Always output valid JSON"""

    @property
    def needs_search(self) -> bool:
        return True

    def _build_prompt(self, task: str, context: dict) -> str:
        theme = context.get("theme", "")
        exclude = context.get("exclude", [])

        exclude_note = ""
        if exclude:
            exclude_note = f"\nExclude these tickers (already owned): {', '.join(exclude)}"

        return f"""Scout for stocks in the {theme} theme.

Search for:
1. Companies that are leaders or pure plays in {theme}
2. Both large cap anchors and smaller high-growth names
3. "Picks and shovels" companies that enable the theme
4. Recent developments and catalysts in the theme
{exclude_note}

{task}

Return your findings as JSON following the format in your instructions."""


_agent = None


def get_thematic_scout() -> ThematicScout:
    global _agent
    if _agent is None:
        _agent = ThematicScout()
    return _agent
