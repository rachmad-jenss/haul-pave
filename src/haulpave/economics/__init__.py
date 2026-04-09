"""Economics module — scenario-based operating cost analysis.

Provides ``compute_economics`` for calculating haul road operating costs
from a ``CostScenario`` input.
"""

from haulpave.economics.engine import EconomicsResult, compute_economics, to_economic_result

__all__ = ["EconomicsResult", "compute_economics", "to_economic_result"]
