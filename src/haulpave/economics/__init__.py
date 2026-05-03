"""Economics module — scenario-based operating cost analysis.

Provides ``compute_economics`` for single-scenario cost calculation and
``compare_scenarios`` for cross-surface RR-based cost comparison.
"""

from haulpave.economics.compare import (
    ComparisonResult,
    RoadScenario,
    ScenarioComparison,
    compare_scenarios,
)
from haulpave.economics.engine import EconomicsResult, compute_economics, to_economic_result

__all__ = [
    "ComparisonResult",
    "EconomicsResult",
    "RoadScenario",
    "ScenarioComparison",
    "compare_scenarios",
    "compute_economics",
    "to_economic_result",
]
