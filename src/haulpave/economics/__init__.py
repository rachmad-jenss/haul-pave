"""Economics module — scenario-based operating cost analysis.

Provides ``compute_economics`` for single-scenario cost calculation,
``compare_scenarios`` for cross-surface RR-based cost comparison, and
``export_comparison_to_excel`` for exporting results to Excel.
"""

from haulpave.economics.compare import (
    ComparisonResult,
    RoadScenario,
    ScenarioComparison,
    compare_scenarios,
)
from haulpave.economics.engine import EconomicsResult, compute_economics, to_economic_result
from haulpave.economics.export import export_comparison_to_excel

__all__ = [
    "ComparisonResult",
    "EconomicsResult",
    "RoadScenario",
    "ScenarioComparison",
    "compare_scenarios",
    "compute_economics",
    "export_comparison_to_excel",
    "to_economic_result",
]
