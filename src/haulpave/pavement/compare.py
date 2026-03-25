"""Comparison engine — USACE TM 5-822-12 CBR vs TRH 14 (CSRA 1985).

Runs both pavement design engines on the same traffic input and subgrade CBR,
returning a side-by-side ComparisonResult with the thickness delta.

Pipeline
--------
1. USACE CBR path (``design_pavement``) — CESA + coverages + USACE CBR curves.
2. TRH 14 path (``compute_trh14``) — USACE coverages + TRH 14 catalog.
3. delta_mm = TRH 14 thickness − USACE thickness.

Confidence label: ``benchmark_tested`` — both sub-engines are benchmark_tested;
comparison arithmetic is verified in tests against known sub-results.

References
----------
- USACE TM 5-822-12 (1990). Flexible Pavement Design for Airfields.
- CSRA (1985). Technical Recommendations for Highways 14 (TRH 14).
- Thompson, R.J. and Visser, A.T. (2006). "The Functional Design of Surface
  Mine Haul Roads." Journal of the South African Institute of Mining and
  Metallurgy, vol. 106, pp. 29–36.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from haulpave.models.traffic import TrafficInput
from haulpave.pavement import PavementResult, design_pavement
from haulpave.pavement.trh14 import TRH14Result, compute_trh14

__all__ = ["ComparisonResult", "compare_methods"]

_DEFAULT_CURVE_ID = "usace_cbr_v1"


@dataclass(frozen=True)
class ComparisonResult:
    """Side-by-side result of USACE CBR vs TRH 14 pavement design.

    Attributes
    ----------
    usace:
        Full result from the USACE TM 5-822-12 CBR design path.
    trh14:
        Full result from the TRH 14 (CSRA 1985) design catalog path.
    delta_mm:
        Thickness difference: ``trh14.total_thickness_mm −
        usace.required_thickness_mm`` [mm].  Positive → TRH 14 requires
        more material; negative → TRH 14 is more conservative (thinner).
    subgrade_cbr:
        Subgrade CBR [%] used for both calculations.
    curve_id:
        USACE CBR curve dataset identifier used.
    method:
        Human-readable method identifier.
    confidence:
        Confidence label.  Inherits from sub-engines: both are
        ``benchmark_tested``.
    """

    usace: PavementResult
    trh14: TRH14Result
    delta_mm: float
    subgrade_cbr: float
    curve_id: str
    method: str = "USACE TM 5-822-12 CBR vs TRH 14 (CSRA 1985) comparison"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"] = (
        "benchmark_tested"
    )


def compare_methods(
    traffic: TrafficInput,
    subgrade_cbr: float,
    curve_id: str = _DEFAULT_CURVE_ID,
) -> ComparisonResult:
    """Compare USACE TM 5-822-12 CBR and TRH 14 pavement design results.

    Runs both engines on identical inputs and returns the combined result
    including the thickness delta.

    Parameters
    ----------
    traffic:
        ``TrafficInput`` containing fleet mix, design life, and working days.
    subgrade_cbr:
        Subgrade CBR value [%].  Must satisfy both engines' constraints:
        within the USACE curve range **and** ≥ 2% (TRH 14 G7 minimum).
    curve_id:
        USACE CBR curve dataset identifier, e.g. ``"usace_cbr_v1"``.
        Defaults to ``"usace_cbr_v1"``.

    Returns
    -------
    ComparisonResult
        Frozen dataclass containing both sub-results and the thickness delta.

    Raises
    ------
    ValueError
        Propagated from either sub-engine — e.g. CBR out of USACE curve
        range, or G8/G9 subgrade (CBR < 2%) not in TRH 14 catalog.
    """
    usace_result = design_pavement(traffic, subgrade_cbr, curve_id)
    trh14_result = compute_trh14(traffic, subgrade_cbr)
    delta = trh14_result.total_thickness_mm - usace_result.required_thickness_mm

    return ComparisonResult(
        usace=usace_result,
        trh14=trh14_result,
        delta_mm=delta,
        subgrade_cbr=subgrade_cbr,
        curve_id=curve_id,
    )
