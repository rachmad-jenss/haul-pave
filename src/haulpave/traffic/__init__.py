"""Traffic module — ESAL/CESA and design coverages.

Implemented in Phase 1 (DAS-99, DAS-100 benchmarks first).
"""

from haulpave.traffic.cesa import CesaResult, compute_cesa
from haulpave.traffic.coverages import CoveragesResult, compute_coverages

__all__ = ["CesaResult", "CoveragesResult", "compute_cesa", "compute_coverages"]
