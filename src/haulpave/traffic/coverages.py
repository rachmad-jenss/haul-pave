"""Design coverages engine — USACE TM 5-822-12 pass-count method.

Method: USACE TM 5-822-12, Flexible Pavement Design for Airfields, para 3-2.

A "coverage" is one complete pass of the design wheel over every point in the
trafficked lane.  The USACE approach converts all wheel loads to equivalent
design-wheel passes using the 4th-power law:

  equiv_passes_per_vehicle_pass = Σ_groups [ positions × (wheel_load / design_wheel_load)^4 ]

Design wheel load
-----------------
The heaviest single-wheel load across every axle group in every vehicle in
the fleet.

Single-wheel load per axle group
---------------------------------
  Single axle (axle_count == 1):
      wheel_load = group_load / tyres_per_axle
      wheel_positions = 1

  Tandem/multi-axle group (axle_count >= 2, dual-tyre stations):
      total_tyre_count = axle_count * 2 * tyres_per_axle
      wheel_load = group_load / (axle_count * 2 * tyres_per_axle)
      wheel_positions = axle_count * tyres_per_axle

Equivalent passes per day per vehicle type
-------------------------------------------
  equiv_passes/day = trips_per_day × 2 (both directions)
                   × Σ_groups [ positions × (wheel_load / design_wheel_load)^4 ]

Total design coverages
-----------------------
  total_coverages = Σ_vehicle_types(equiv_passes/day) × working_days × design_life

Confidence label: ``benchmark_tested`` — matches published hand-calc within ±2 %.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from haulpave.models.traffic import TrafficInput
from haulpave.models.vehicle import AxleGroup

__all__ = ["CoveragesResult", "compute_coverages"]


@dataclass(frozen=True)
class CoveragesResult:
    """Result of a design coverages calculation.

    Attributes
    ----------
    total_coverages:
        Total equivalent design-wheel coverages over the full design life.
    design_wheel_load_kn:
        Maximum single-wheel load in the fleet [kN] — the design vehicle.
    method:
        Human-readable method identifier.
    confidence:
        Confidence label following the project plan §4.3 convention.
    """

    total_coverages: float
    design_wheel_load_kn: float
    method: str = "USACE TM 5-822-12 pass-count method"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"] = (
        "benchmark_tested"
    )


def _wheel_load_kn(group: AxleGroup) -> float:
    """Compute the single-wheel load for one axle group [kN].

    For a single axle (axle_count == 1) the total tyre count is
    simply ``tyres_per_axle`` and the wheel load is the group load
    divided by that count.

    For a tandem or multi-axle group (axle_count >= 2) the tyres are
    arranged as dual-tyre stations: each station carries two tyres that
    share one contact patch.  The total effective tyre count is therefore
    ``axle_count * 2 * tyres_per_axle`` and the single-wheel load is the
    group load divided by that count.
    """
    if group.axle_count == 1:
        return group.gross_load_kn / group.tyres_per_axle
    # Dual-tyre tandem/multi-axle: factor of 2 for paired tyre stations
    return group.gross_load_kn / (group.axle_count * 2 * group.tyres_per_axle)


def _wheel_positions(group: AxleGroup) -> int:
    """Number of independent wheel-track positions for one axle group.

    A single axle contributes 1 position (one tyre track on the design
    line, regardless of how many tyres it carries).

    A tandem/multi-axle group contributes ``axle_count * tyres_per_axle``
    positions (each dual-tyre station is one independent position on the
    pavement surface).
    """
    if group.axle_count == 1:
        return 1
    return group.axle_count * group.tyres_per_axle


def _design_wheel_load_kn(traffic: TrafficInput) -> float:
    """Return the maximum single-wheel load [kN] across the entire fleet."""
    max_load: float = 0.0
    for fleet_unit in traffic.fleet:
        for group in fleet_unit.vehicle.axle_groups:
            load = _wheel_load_kn(group)
            if load > max_load:
                max_load = load
    return max_load


def _equiv_passes_per_day(
    axle_groups: list[AxleGroup],
    trips_per_day: float,
    design_wheel_load: float,
) -> float:
    """Equivalent design-wheel passes per day for one vehicle type.

    Both directions are counted (multiplier of 2).

    Parameters
    ----------
    axle_groups:
        Axle groups of this vehicle.
    trips_per_day:
        One-way trips per day.
    design_wheel_load:
        Fleet design wheel load [kN].

    Returns
    -------
    float
        Equivalent design-wheel passes per day.
    """
    group_contribution: float = 0.0
    for group in axle_groups:
        wl = _wheel_load_kn(group)
        positions = _wheel_positions(group)
        ratio = wl / design_wheel_load
        group_contribution += positions * (ratio**4)

    return trips_per_day * 2.0 * group_contribution


def compute_coverages(traffic: TrafficInput) -> CoveragesResult:
    """Compute design coverages for a given traffic input.

    Implements the USACE TM 5-822-12 pass-count method.  The design wheel
    load is the heaviest single-wheel load in the fleet; all other vehicles
    are weighted by the 4th power of the wheel-load ratio.

    Parameters
    ----------
    traffic:
        ``TrafficInput`` containing the fleet mix, design life, and
        working days per year.

    Returns
    -------
    CoveragesResult
        Frozen dataclass with ``total_coverages``, ``design_wheel_load_kn``,
        ``method``, and ``confidence``.
    """
    design_wheel_load = _design_wheel_load_kn(traffic)

    total_equiv_passes_per_day: float = 0.0
    for fleet_unit in traffic.fleet:
        total_equiv_passes_per_day += _equiv_passes_per_day(
            fleet_unit.vehicle.axle_groups,
            fleet_unit.trips_per_day,
            design_wheel_load,
        )

    total_coverages = (
        total_equiv_passes_per_day * traffic.working_days_per_year * traffic.design_life_years
    )

    return CoveragesResult(
        total_coverages=total_coverages,
        design_wheel_load_kn=design_wheel_load,
    )
