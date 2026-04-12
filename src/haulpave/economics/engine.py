"""Operating cost calculation engine for mine haul roads.

Method: Simple unit-cost summation per trip — fuel, tyre wear, maintenance,
and operator cost components.

    cost_per_trip = fuel + tyre + maintenance + operator

Where:
    fuel       = fuel_consumption_l_per_km × haul_distance_km × fuel_cost_per_litre
    tyre       = tyre_cost_per_hour × trip_time_hours
    maintenance = maintenance_cost_per_km × haul_distance_km
    operator   = operator_cost_per_hour × trip_time_hours

    trip_time_hours = haul_distance_km / average_speed_kmh

Confidence label: ``method_implemented`` — straightforward arithmetic,
not yet validated against a published benchmark dossier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from haulpave.models.economics import CostScenario, EconomicResult


@dataclass(frozen=True)
class EconomicsResult:
    """Detailed breakdown of an operating cost calculation.

    Attributes
    ----------
    scenario_id:
        Identifier from the input scenario.
    cost_per_trip:
        Total cost per one-way trip [currency].
    cost_per_tonne_km:
        Unit transport cost [currency / (tonne · km)].
    fuel_cost_per_trip:
        Fuel component of cost per trip [currency].
    tyre_cost_per_trip:
        Tyre wear component of cost per trip [currency].
    maintenance_cost_per_trip:
        Maintenance component of cost per trip [currency].
    operator_cost_per_trip:
        Operator component of cost per trip [currency].
    trips_per_year:
        Annual trip count (0 if not provided).
    annual_cost:
        Annual operating cost (0 if trips_per_year not provided).
    currency:
        ISO 4217 currency code.
    method:
        Human-readable method identifier.
    confidence:
        Confidence label following the project plan §4.3 convention.
    """

    scenario_id: str
    cost_per_trip: float
    cost_per_tonne_km: float
    fuel_cost_per_trip: float
    tyre_cost_per_trip: float
    maintenance_cost_per_trip: float
    operator_cost_per_trip: float
    trips_per_year: float
    annual_cost: float
    currency: str
    method: str = "haulpave-economics-v1"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"] = (
        "method_implemented"
    )


def compute_economics(
    scenario: CostScenario,
    trips_per_day: float = 0.0,
    working_days_per_year: int = 250,
) -> EconomicsResult:
    """Compute operating cost for a haul road scenario.

    Parameters
    ----------
    scenario:
        ``CostScenario`` containing haul geometry, fleet parameters,
        and cost assumptions.
    trips_per_day:
        One-way trips per day for annual cost calculation.
        If 0, ``trips_per_year`` and ``annual_cost`` are returned as 0.
    working_days_per_year:
        Operating days per year (default 250).

    Returns
    -------
    EconomicsResult
        Frozen dataclass with cost breakdown and optional annual totals.
    """
    if trips_per_day < 0:
        raise ValueError("trips_per_day must be >= 0")
    if trips_per_day > 0 and working_days_per_year <= 0:
        raise ValueError("working_days_per_year must be > 0 when trips_per_day is provided")

    a = scenario.assumptions
    trip_time_hours = scenario.haul_distance_km / scenario.average_speed_kmh

    fuel = scenario.fuel_consumption_l_per_km * scenario.haul_distance_km * a.fuel_cost_per_litre
    tyre = a.tyre_cost_per_hour * trip_time_hours
    maintenance = a.maintenance_cost_per_km * scenario.haul_distance_km
    operator = a.operator_cost_per_hour * trip_time_hours

    cost_per_trip = fuel + tyre + maintenance + operator
    cost_per_tonne_km = cost_per_trip / (scenario.payload_t * scenario.haul_distance_km)

    trips_year = trips_per_day * working_days_per_year if trips_per_day > 0 else 0.0
    annual = cost_per_trip * trips_year

    return EconomicsResult(
        scenario_id=scenario.scenario_id,
        cost_per_trip=cost_per_trip,
        cost_per_tonne_km=cost_per_tonne_km,
        fuel_cost_per_trip=fuel,
        tyre_cost_per_trip=tyre,
        maintenance_cost_per_trip=maintenance,
        operator_cost_per_trip=operator,
        trips_per_year=trips_year,
        annual_cost=annual,
        currency=a.currency,
    )


def to_economic_result(result: EconomicsResult) -> EconomicResult:
    """Convert detailed EconomicsResult to the Pydantic EconomicResult model."""
    return EconomicResult(
        scenario_id=result.scenario_id,
        cost_per_tonne_km=result.cost_per_tonne_km,
        cost_per_trip=result.cost_per_trip,
        trips_per_year=result.trips_per_year,
        annual_cost=result.annual_cost,
        currency=result.currency,
        method=result.method,
    )
