"""TRH 14 pavement design engine — South African haul road method.

Method: CSRA TRH 14 (1985) design catalog for unpaved haul roads, as
described in Thompson & Visser (2006).  The method classifies the subgrade
into G1–G9 material classes based on CBR and looks up total pavement
thickness from the TRH 14 design catalog using log-linear interpolation
on the design-coverages axis.

Design traffic is computed via the USACE TM 5-822-12 design-coverages method
(same ``compute_coverages`` engine used by the USACE CBR path).

Confidence label: ``benchmark_tested`` — passes bench_05.

References
----------
- CSRA (1985). Technical Recommendations for Highways 14 (TRH 14):
  Guidelines for Road Construction Materials. Committee of State Road
  Authorities, Pretoria.
- Thompson, R.J. and Visser, A.T. (2006). "The Functional Design of Surface
  Mine Haul Roads." Journal of the South African Institute of Mining and
  Metallurgy, vol. 106, pp. 29–36.
- USACE TM 5-822-12 (1990). Design-coverages method (for traffic loading).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from haulpave.models.traffic import TrafficInput
from haulpave.traffic.coverages import compute_coverages

__all__ = ["TRH14Result", "cbr_to_material_class", "compute_trh14"]

_CATALOG_PATH = Path(__file__).parent.parent / "design" / "curves" / "trh14_catalog_v1.json"

# G-class lower-CBR boundaries in descending order (strongest first).
# Boundary is inclusive on the lower end: CBR=7 → G5 (not G6).
_G_CLASS_BOUNDS: list[tuple[str, float]] = [
    ("G1", 80.0),
    ("G2", 45.0),
    ("G3", 25.0),
    ("G4", 15.0),
    ("G5", 7.0),
    ("G6", 4.0),
    ("G7", 2.0),
    ("G8", 1.5),
    ("G9", 0.0),
]


def cbr_to_material_class(cbr: float) -> str:
    """Map subgrade CBR (%) to TRH 14 G-class material classification.

    Boundaries are inclusive on the lower bound (TRH 14, Table 2):
    G1: CBR ≥ 80,  G2: CBR ≥ 45,  G3: CBR ≥ 25,  G4: CBR ≥ 15,
    G5: CBR ≥ 7,   G6: CBR ≥ 4,   G7: CBR ≥ 2,   G8: CBR ≥ 1.5,
    G9: CBR < 1.5.

    Parameters
    ----------
    cbr:
        Subgrade CBR value [%].  Must be ≥ 0.

    Returns
    -------
    str
        G-class label, e.g. ``"G5"``.

    Raises
    ------
    ValueError
        If ``cbr`` is negative.
    """
    if cbr < 0:
        raise ValueError(f"CBR must be >= 0, got {cbr}")
    for g_class, min_cbr in _G_CLASS_BOUNDS:
        if cbr >= min_cbr:
            return g_class
    return "G9"  # pragma: no cover — G9 bound=0.0 catches all remaining values


def _load_catalog() -> dict[str, Any]:
    """Load TRH 14 design catalog JSON."""
    with _CATALOG_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)  # type: ignore[no-any-return]


def _interpolate_catalog(
    thickness_values: list[float],
    coverage_levels: list[int],
    coverages: float,
) -> float:
    """Log-linear interpolation of thickness at a given coverage level.

    Coverage values outside the catalog range are silently clamped to the
    nearest boundary — consistent with the USACE interpolation convention.

    Parameters
    ----------
    thickness_values:
        Thickness [mm] at each ``coverage_levels`` knot for one G-class.
    coverage_levels:
        Ordered list of coverage knot points (must match ``thickness_values``).
    coverages:
        Design coverages.  Clamped to ``[coverage_levels[0], coverage_levels[-1]]``.

    Returns
    -------
    float
        Interpolated total pavement thickness [mm].
    """
    cov_clamped = max(float(coverage_levels[0]), min(float(coverage_levels[-1]), coverages))
    log_cov = math.log10(cov_clamped)
    log_levels = [math.log10(float(c)) for c in coverage_levels]

    # Find the enclosing bracket
    for i in range(len(log_levels) - 1):
        if log_levels[i] <= log_cov <= log_levels[i + 1]:
            span = log_levels[i + 1] - log_levels[i]
            frac = (log_cov - log_levels[i]) / span if span > 0 else 0.0
            return thickness_values[i] + frac * (thickness_values[i + 1] - thickness_values[i])

    # Clamped value equals the upper boundary exactly
    return float(thickness_values[-1])


@dataclass(frozen=True)
class TRH14Result:
    """Result of a TRH 14 pavement design calculation.

    Attributes
    ----------
    material_class:
        TRH 14 G-class of the subgrade, e.g. ``"G5"``.
    total_thickness_mm:
        Required total compacted pavement thickness from the TRH 14 catalog [mm].
    total_coverages:
        Total equivalent design-wheel coverages over the full design life
        (USACE TM 5-822-12 method).
    design_wheel_load_kn:
        Maximum single-wheel load in the fleet [kN] — the design vehicle.
    method:
        Human-readable method identifier.
    confidence:
        Confidence label following the project plan §4.3 convention.
    """

    material_class: str
    total_thickness_mm: float
    total_coverages: float
    design_wheel_load_kn: float
    method: str = "TRH 14 (CSRA 1985) design catalog + USACE design-coverages"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"] = (
        "benchmark_tested"
    )


def compute_trh14(traffic: TrafficInput, subgrade_cbr: float) -> TRH14Result:
    """Design pavement thickness using the TRH 14 (CSRA 1985) method.

    Pipeline:
    1. Compute design coverages — USACE TM 5-822-12 (``compute_coverages``).
    2. Classify subgrade CBR → G-class (TRH 14, Table 2).
    3. Look up total thickness from TRH 14 catalog
       (log-linear interpolation on coverages axis).

    Parameters
    ----------
    traffic:
        ``TrafficInput`` containing fleet mix, design life, and working days.
    subgrade_cbr:
        Subgrade CBR value [%].  Must be ≥ 0.

    Returns
    -------
    TRH14Result
        Frozen dataclass with all pipeline outputs and metadata.

    Raises
    ------
    ValueError
        If ``subgrade_cbr`` is negative, or the resulting G-class (G8 or G9)
        is not in the design catalog (subgrade improvement required).
    """
    cov_result = compute_coverages(traffic)
    g_class = cbr_to_material_class(subgrade_cbr)

    catalog = _load_catalog()
    thickness_table: dict[str, list[float]] = catalog["thickness_mm"]

    if g_class not in thickness_table:
        raise ValueError(
            f"Subgrade G-class '{g_class}' (CBR={subgrade_cbr}%) is not in the TRH 14 "
            f"design catalog. G8 and G9 subgrades require improvement works before "
            f"pavement design. Improve the subgrade to at least G7 (CBR ≥ 2%)."
        )

    coverage_levels: list[int] = catalog["coverage_levels"]
    thickness_values: list[float] = thickness_table[g_class]

    thickness = _interpolate_catalog(thickness_values, coverage_levels, cov_result.total_coverages)

    return TRH14Result(
        material_class=g_class,
        total_thickness_mm=thickness,
        total_coverages=cov_result.total_coverages,
        design_wheel_load_kn=cov_result.design_wheel_load_kn,
    )
