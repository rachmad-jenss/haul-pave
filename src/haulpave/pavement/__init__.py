"""Pavement design engine — CBR thickness via USACE TM 5-822-12 curves.

Method: USACE TM 5-822-12 (1990) Figure 1 CBR design curves, using PCHIP
interpolation from digitized curve data.  Orchestrates the CESA engine
(AASHTO 4th-power law) and the design-coverages engine (USACE pass-count
method) then maps the result onto the CBR thickness curve.

Confidence label: ``high`` — passes bench_03 and bench_04.

References
----------
- USACE TM 5-822-12 (1990). Flexible Pavement Design for Airfields.
  Figure 1: CBR design curves.
- AASHTO (1993). Guide for Design of Pavement Structures, 4th edition.
- USACE EM 1110-3-141 (1987). Pavement Design for Roads, Streets, and Open
  Storage Areas, Flexible Design.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from haulpave.pavement.trh14 import TRH14Result

from haulpave.models.traffic import TrafficInput
from haulpave.traffic.cesa import compute_cesa
from haulpave.traffic.coverages import compute_coverages
from haulpave.utils.interpolation import interpolate_thickness, load_curve_data

__all__ = [
    "ComparisonResult",
    "PavementResult",
    "compare_methods",
    "design_pavement",
    "cbr_thickness_from_coverages",
    "trh14_thickness_from_coverages",
]


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
    total_thickness_mm:
        Alias for ``required_thickness_mm``.  Total pavement thickness [mm].
    design_wheel_load_kn:
        Maximum single-wheel load in the fleet [kN] — the design vehicle.
    subgrade_cbr:
        Subgrade CBR value [%] used for the design.
    layers:
        Layer breakdown (empty for USACE CBR method; populated when
        layer-specific design methods are used).
    was_clamped:
        True if design coverages exceeded the curve range and were clamped
        to the nearest boundary.
    method:
        Human-readable method identifier.
    confidence:
        Confidence label following the project plan §4.3 convention.
    """

    total_cesa: float
    total_coverages: float
    required_thickness_mm: float
    design_wheel_load_kn: float
    total_thickness_mm: float = 0.0
    subgrade_cbr: float = 0.0
    layers: tuple[dict[str, Any], ...] = ()
    was_clamped: bool = False
    method: str = "USACE TM 5-822-12 CBR design curves + AASHTO 4th-power LEF"
    confidence: Literal["high", "medium", "low"] = "high"


def design_pavement(
    traffic: TrafficInput,
    subgrade_cbr: float,
    curve_id: str = "usace_cbr_v1",
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
    Coverage values that exceed the curve's tabulated range are
    clamped to the curve boundary.  ``result.was_clamped`` is ``True``
    when clamping occurs.
    """
    cesa_result = compute_cesa(traffic)
    cov_result = compute_coverages(traffic)
    curve_data = load_curve_data(curve_id)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        thickness, _was_clamped = interpolate_thickness(
            curve_data,
            cbr=subgrade_cbr,
            coverages=cov_result.total_coverages,
        )
    was_clamped = _was_clamped or any("clamped" in str(msg.message).lower() for msg in w)
    return PavementResult(
        total_cesa=cesa_result.total_cesa,
        total_coverages=cov_result.total_coverages,
        required_thickness_mm=thickness,
        total_thickness_mm=thickness,
        design_wheel_load_kn=cov_result.design_wheel_load_kn,
        subgrade_cbr=subgrade_cbr,
        was_clamped=was_clamped,
    )


# ---------------------------------------------------------------------------
# Bridge adapter functions — accept pre-computed design_coverages from the RPC
# layer instead of a full TrafficInput (used by haul-calc bridge.py).
# ---------------------------------------------------------------------------


def cbr_thickness_from_coverages(
    subgrade_cbr: float,
    design_coverages: float,
    curve_id: str = "usace_cbr_v1",
) -> float:
    """Return required CBR pavement thickness from pre-computed design coverages.

    Unlike :func:`design_pavement`, this adapter skips the CESA / coverages
    pipeline and feeds ``design_coverages`` directly into the USACE CBR curve
    interpolation.  Intended for use by the haul-calc JSON-RPC bridge when the
    front-end supplies ``design_coverages`` directly.

    Parameters
    ----------
    subgrade_cbr:
        Subgrade CBR [%].  Must be within the supported curve range.
    design_coverages:
        Pre-computed design coverages (equivalent wheel passes).  Must be > 0.
    curve_id:
        Digitized curve dataset identifier (default ``"usace_cbr_v1"``).

    Returns
    -------
    float
        Required total pavement thickness [mm].
    """
    curve_data = load_curve_data(curve_id)
    thickness, _was_clamped = interpolate_thickness(
        curve_data, cbr=subgrade_cbr, coverages=design_coverages
    )
    return thickness


def trh14_thickness_from_coverages(
    subgrade_cbr: float,
    design_coverages: float,
) -> TRH14Result:
    """Return TRH 14 pavement thickness from subgrade CBR and pre-computed coverages.

    Adapter for the haul-calc JSON-RPC bridge: accepts raw ``design_coverages``
    directly instead of computing them from a ``TrafficInput``.

    Parameters
    ----------
    subgrade_cbr:
        Subgrade CBR [%].  Must be ≥ 0.
    design_coverages:
        Pre-computed design coverages.  Must be > 0.

    Returns
    -------
    TRH14Result
        Frozen dataclass with material class, thickness, and input coverages.

    Raises
    ------
    ValueError
        If ``subgrade_cbr`` < 0, or the resulting G-class (G8/G9) is not in
        the TRH 14 design catalog.
    """
    from haulpave.pavement.trh14 import (
        TRH14Result,
        cbr_to_material_class,
        interpolate_catalog,
        load_catalog,
    )

    if design_coverages <= 0:
        raise ValueError(f"design_coverages must be > 0, got {design_coverages}")

    g_class = cbr_to_material_class(subgrade_cbr)
    catalog = load_catalog()
    thickness_table: dict[str, list[float]] = catalog["thickness_mm"]

    if g_class not in thickness_table:
        raise ValueError(
            f"Subgrade G-class '{g_class}' (CBR={subgrade_cbr}%) is not in the TRH 14 "
            f"design catalog. Improve the subgrade to at least G7 (CBR ≥ 2%)."
        )

    coverage_levels: list[int] = catalog["coverage_levels"]
    thickness_values: list[float] = thickness_table[g_class]
    thickness, was_clamped = interpolate_catalog(
        thickness_values, coverage_levels, design_coverages
    )

    return TRH14Result(
        material_class=g_class,
        total_thickness_mm=thickness,
        total_coverages=design_coverages,
        design_wheel_load_kn=0.0,  # unknown when using pre-computed coverages
        was_clamped=was_clamped,
    )


def __getattr__(name: str) -> Any:
    """Lazy re-export to break circular import between this module and compare."""
    if name in ("ComparisonResult", "compare_methods"):
        import haulpave.pavement.compare as _mod

        return getattr(_mod, name)
    if name == "TRH14Result":
        from haulpave.pavement.trh14 import TRH14Result

        return TRH14Result
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
