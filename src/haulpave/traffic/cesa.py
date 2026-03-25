"""CESA (Cumulative Equivalent Standard Axles) engine.

Method: AASHTO (1993) 4th-power Load Equivalency Factor (LEF).

Reference
---------
AASHTO (1993) Guide for Design of Pavement Structures, 4th edition.

4th Power Law
-------------
  Single axle (axle_count == 1):
      LEF = (gross_load_kN / 80.0) ** 4

  Tandem group (axle_count == 2):
      LEF = (gross_load_kN / 160.0) ** 4 * 2

  General multi-axle group (axle_count == n):
      standard_load = 80.0 * n
      LEF = (gross_load_kN / standard_load) ** 4 * n

CESA per vehicle per direction
-------------------------------
  CESA = trips_per_day × total_LEF × working_days_per_year × design_life_years

Total CESA = sum over all FleetUnits.

Confidence label: ``benchmark_tested`` — matches published hand-calc within ±1 %.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from haulpave.models.traffic import TrafficInput
from haulpave.models.vehicle import AxleGroup

__all__ = ["CesaResult", "compute_cesa"]

_STANDARD_SINGLE_AXLE_KN: float = 80.0
_STANDARD_AXLE_KN_PER_AXLE: float = 80.0  # 80 kN per axle in a group


@dataclass(frozen=True)
class CesaResult:
    """Result of a CESA calculation.

    Attributes
    ----------
    total_cesa:
        Cumulative Equivalent Standard Axles over the full design life.
    method:
        Human-readable method identifier.
    confidence:
        Confidence label following the project plan §4.3 convention.
    """

    total_cesa: float
    method: str = "AASHTO 4th-power LEF (AASHTO 1993)"
    confidence: Literal[
        "benchmark_tested", "method_implemented", "experimental"
    ] = "benchmark_tested"


def _lef_for_axle_group(group: AxleGroup) -> float:
    """Compute Load Equivalency Factor for one axle group.

    For a group with *n* axles the standard reference load is 80 × n kN
    (i.e. 80 kN/axle).  The 4th-power law is applied to the ratio of the
    actual group load to the reference group load, then multiplied by *n*
    so that the result is expressed in units of standard single-axle passes.

    Examples
    --------
    Single axle, 80 kN  →  (80/80)^4 × 1 = 1.0   ✓ standard axle
    Tandem group, 160 kN → (160/160)^4 × 2 = 2.0  ✓ standard tandem
    """
    n = group.axle_count
    standard_load_kn = _STANDARD_AXLE_KN_PER_AXLE * n
    return (group.gross_load_kn / standard_load_kn) ** 4 * n


def _total_lef_per_vehicle(axle_groups: list[AxleGroup]) -> float:
    """Sum LEF across all axle groups of one vehicle."""
    return sum(_lef_for_axle_group(g) for g in axle_groups)


def compute_cesa(traffic: TrafficInput) -> CesaResult:
    """Compute Cumulative Equivalent Standard Axles for a given traffic input.

    Parameters
    ----------
    traffic:
        ``TrafficInput`` containing the fleet mix, design life, and
        working days per year.

    Returns
    -------
    CesaResult
        Frozen dataclass with ``total_cesa``, ``method``, and ``confidence``.

    Notes
    -----
    The calculation follows the AASHTO (1993) 4th-power law without applying
    a directional distribution factor — the ``trips_per_day`` field in
    ``FleetUnit`` is assumed to already represent one-way (uni-directional)
    passes on the design section.
    """
    total: float = 0.0

    for fleet_unit in traffic.fleet:
        lef_per_trip = _total_lef_per_vehicle(fleet_unit.vehicle.axle_groups)
        cesa_contribution = (
            fleet_unit.trips_per_day
            * lef_per_trip
            * traffic.working_days_per_year
            * traffic.design_life_years
        )
        total += cesa_contribution

    return CesaResult(total_cesa=total)
