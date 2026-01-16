"""
Shrestha Capital - Risk Pipeline

Orchestrates comprehensive portfolio risk analysis:
1. Stress testing (historical scenarios)
2. Value at Risk (VaR)
3. Monte Carlo simulation
4. Correlation/diversification analysis

Produces a complete risk report.
"""

import asyncio
from typing import Optional, List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.risk.stress_test_agent import get_stress_test_agent
from agents.risk.var_agent import get_var_agent
from agents.risk.monte_carlo_agent import get_monte_carlo_agent
from agents.risk.correlation_agent import get_correlation_agent


class RiskPipeline:
    """
    Orchestrates complete portfolio risk analysis.

    Usage:
        pipeline = RiskPipeline()
        report = await pipeline.analyze(positions, portfolio_value)
    """

    def __init__(self):
        self.stress_test_agent = get_stress_test_agent()
        self.var_agent = get_var_agent()
        self.monte_carlo_agent = get_monte_carlo_agent()
        self.correlation_agent = get_correlation_agent()

    async def analyze(
        self,
        positions: List[Dict],
        portfolio_value: float = 1000000,
        run_full: bool = True
    ) -> dict:
        """
        Run complete risk analysis on a portfolio.

        Args:
            positions: List of position dicts [{ticker, weight, ...}]
            portfolio_value: Total portfolio value
            run_full: Run all agents (False = just stress test + VaR)

        Returns:
            Complete risk report
        """
        print(f"\n{'='*60}")
        print("RISK PIPELINE: Analyzing Portfolio Risk")
        print(f"{'='*60}\n")

        context = {
            "positions": positions,
            "portfolio_value": portfolio_value
        }

        # Step 1: Run risk agents in parallel
        if run_full:
            print("Running all risk agents in parallel...\n")
            tasks = [
                self._run_agent("Stress Test", self.stress_test_agent, context),
                self._run_agent("VaR", self.var_agent, context),
                self._run_agent("Monte Carlo", self.monte_carlo_agent, context),
                self._run_agent("Correlation", self.correlation_agent, context),
            ]
        else:
            print("Running core risk agents...\n")
            tasks = [
                self._run_agent("Stress Test", self.stress_test_agent, context),
                self._run_agent("VaR", self.var_agent, context),
            ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect results
        stress_test = results[0] if not isinstance(results[0], Exception) else {"_error": str(results[0])}
        var = results[1] if not isinstance(results[1], Exception) else {"_error": str(results[1])}

        monte_carlo = {}
        correlation = {}
        if run_full and len(results) > 2:
            monte_carlo = results[2] if not isinstance(results[2], Exception) else {"_error": str(results[2])}
            correlation = results[3] if not isinstance(results[3], Exception) else {"_error": str(results[3])}

        # Step 2: Compile risk report
        print("\nCompiling risk report...\n")

        report = {
            "portfolio": {
                "positions_count": len(positions),
                "total_value": f"${portfolio_value:,.0f}",
                "positions": positions
            },
            "stress_tests": stress_test,
            "var": var,
            "monte_carlo": monte_carlo if run_full else None,
            "correlations": correlation if run_full else None,
            "summary": self._generate_summary(stress_test, var, monte_carlo, correlation),
            "risk_flags": self._identify_flags(stress_test, var, monte_carlo, correlation),
            "recommendations": self._compile_recommendations(stress_test, var, monte_carlo, correlation)
        }

        print(f"{'='*60}")
        print("RISK ANALYSIS COMPLETE")
        print(f"{'='*60}\n")

        return report

    async def _run_agent(self, name: str, agent, context: dict) -> dict:
        """Run a single risk agent"""
        print(f"  → Running {name} agent...")
        try:
            result = await agent.run(
                task="Analyze portfolio risk",
                context=context
            )
            print(f"  ✓ {name} complete")
            return result
        except Exception as e:
            print(f"  ✗ {name} failed: {str(e)[:100]}")
            raise

    def _generate_summary(self, stress: dict, var: dict, mc: dict, corr: dict) -> dict:
        """Generate executive risk summary"""
        return {
            "worst_case_drawdown": stress.get("worst_case_scenario", {}).get("portfolio_decline", "N/A"),
            "daily_var_95": var.get("var_metrics", {}).get("daily_var_95", {}).get("percent", "N/A"),
            "probability_of_loss": mc.get("outcome_probabilities", {}).get("prob_loss_gt_10pct", "N/A") if mc else "N/A",
            "effective_positions": corr.get("portfolio_summary", {}).get("effective_positions", "N/A") if corr else "N/A",
            "overall_risk_level": self._assess_overall_risk(stress, var, mc, corr)
        }

    def _assess_overall_risk(self, stress: dict, var: dict, mc: dict, corr: dict) -> str:
        """Assess overall portfolio risk level"""
        # Simple heuristic based on worst case and VaR
        worst = stress.get("worst_case_scenario", {}).get("portfolio_decline", "-50%")
        try:
            worst_pct = abs(float(worst.replace("%", "").replace("-", "")))
        except:
            worst_pct = 50

        if worst_pct > 50:
            return "HIGH"
        elif worst_pct > 35:
            return "MODERATE-HIGH"
        elif worst_pct > 25:
            return "MODERATE"
        else:
            return "LOW-MODERATE"

    def _identify_flags(self, stress: dict, var: dict, mc: dict, corr: dict) -> List[str]:
        """Identify key risk flags"""
        flags = []

        # From stress test
        if stress.get("risk_flags"):
            flags.extend(stress["risk_flags"][:2])

        # From correlation
        if corr and corr.get("diversification_assessment", {}).get("score", "5/10").startswith(("3", "4", "5")):
            flags.append("Diversification quality needs improvement")

        # From VaR
        var_pct = var.get("var_metrics", {}).get("daily_var_95", {}).get("percent", "0%")
        try:
            if float(var_pct.replace("%", "")) > 3:
                flags.append(f"High daily VaR of {var_pct}")
        except:
            pass

        return flags[:5]  # Limit to top 5 flags

    def _compile_recommendations(self, stress: dict, var: dict, mc: dict, corr: dict) -> List[str]:
        """Compile risk reduction recommendations"""
        recs = []

        if stress.get("recommendations"):
            recs.extend(stress["recommendations"][:2])

        if var.get("recommendations"):
            recs.extend(var["recommendations"][:1])

        if corr and corr.get("recommendations"):
            recs.extend(corr["recommendations"][:2])

        return list(set(recs))[:5]  # Dedupe and limit


# Convenience function
async def analyze_portfolio_risk(
    positions: List[Dict],
    portfolio_value: float = 1000000
) -> dict:
    """Analyze portfolio risk using the full pipeline"""
    pipeline = RiskPipeline()
    return await pipeline.analyze(positions, portfolio_value)
