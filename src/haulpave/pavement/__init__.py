"""Pavement design engine — CBR thickness via USACE TM 5-822-12 curves.

Method: USACE TM 5-822-12 (1990) Figure 1 CBR design curves, using PCHIP
interpolation from digitized curve data.  Orchestrates the CESA engine
(AASHTO 4th-power law) and the design-coverages engine (USACE pass-count
method) then maps the result onto the CBR thickness curve.

Confidence label: ``benchmark_tested`` — passes bench_03 and bench_04.

References
----------
- USACE TM 5-822-12 (1990). Flexible Pavement Design for Airfields.
  Figure 1: CBR design curves.
- AASHTO (1993). Guide for Design of Pavement Structures, 4th edition.
- USACE EM 1110-3-141 (1987). Pavement Design for Roads, Streets, and Open
  Storage Areas, Flexible Design.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from haulpave.models.traffic import TrafficInput
from haulpave.traffic.cesa import compute_cesa
from haulpave.traffic.coverages import compute_coverages
from haulpave.utils.interpolation import interpolate_thickness, load_curve_data

__all__ = ["PavementResult", "design_pavement"]


@dataclass(frozen=True)
class PavementResult:
    """Result of a pavement design calculation.

    Attributes
    ----------
    total_cesa:
        Cumulative Equivalent Standard Axles over the full design life.
    total_coverages:
        Total equivalent design-wheel coverages over the full design life.
    required_thickness_mm:
        Required total pavement thickness from the CBR design curve [mm].
    design_wheel_load_kn:
        Maximum single-wheel load in the fleet [kN] — the design vehicle.
    method:
        Human-readable method identifier.
    confidence:
        Confidence label following the project plan §4.3 convention.
    """

    total_cesa: float
    total_coverages: float
    required_thickness_mm: float
    design_wheel_load_kn: float
    method: str = "USACE TM 5-822-12 CBR design curves + AASHTO 4th-power LEF"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"] = (
        "benchmark_tested"
    )


def design_pavement(
    traffic: TrafficInput,
    subgrade_cbr: float,
    curve_id: str,
) -> PavementResult:
    """Design pavement thickness using the USACE TM 5-822-12 CBR method.

    Orchestrates three pipeline stages:
    1. CESA — AASHTO 4th-power LEF (``compute_cesa``).
    2. Design coverages — USACE TM 5-822-12 pass-count method
       (``compute_coverages``).
    3. Required thickness — PCHIP interpolation on USACE CBR curves
       (``interpolate_thickness``).

    Parameters
    ----------
    traffic:
        ``TrafficInput`` containing fleet mix, design life, and working days.
    subgrade_cbr:
        Subgrade CBR value [%].  Must be within the range of the selected
        curve (raises ``ValueError`` if out of range).
    curve_id:
        Digitized curve dataset identifier, e.g. ``"usace_cbr_v1"``.
        Loads ``<curve_id>.json`` from ``src/haulpave/design/curves/``.

    Returns
    -------
    PavementResult
        Frozen dataclass with all pipeline outputs and metadata.

    Notes
    -----
    Coverage values that exceed the curve's tabulated range are silently
    clamped to the curve boundary by ``interpolate_thickness``.  This is the
    correct engineering interpretation: the design is governed by the worst
    case represented in the source chart.
    """
    cesa_result = compute_cesa(traffic)
    cov_result = compute_coverages(traffic)
    curve_data = load_curve_data(curve_id)
    thickness = interpolate_thickness(
        curve_data,
        cbr=subgrade_cbr,
        coverages=cov_result.total_coverages,
    )
    return PavementResult(
        total_cesa=cesa_result.total_cesa,
        total_coverages=cov_result.total_coverages,
        required_thickness_mm=thickness,
        design_wheel_load_kn=cov_result.design_wheel_load_kn,
    )
