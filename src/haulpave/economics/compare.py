"""Scenario comparison engine — operating cost differential by road surface type.

Method: Rolling-resistance (RR) linear cost model.  Each surface carries a
characteristic RR coefficient; operating costs scale linearly with RR via
calibrated empirical coefficients derived from mine haul-road data.

Rolling-resistance coefficients:
    asphalt  : 1.5 %  (well-maintained sealed surface)
    concrete : 1.2 %  (rigid slab — lowest RR)
    gravel   : 4.0 %  (crushed-stone haul road, typical mine condition)

Calibrated linear model (per vehicle-km):
    fuel_l_per_km    = 2.042 + 29.2 × RR
    tyre_usd_per_km  = 0.128 + 92.8 × RR
    maint_usd_per_km = 0.144 + 30.4 × RR

Where RR is expressed as a fraction (e.g. 0.015 for 1.5 %).

Annual cost = cost_per_km × haul_distance_km × trips_per_day × working_days_per_year

Confidence label: ``experimental`` — linear RR coefficients are calibrated
industry approximations; not validated against a published benchmark dossier.
Model validates directionally: gravel > asphalt > concrete in all categories.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ConfidenceLabel = Literal["benchmark_tested", "method_implemented", "experimental"]

__all__ = ["ComparisonResult", "RoadScenario", "ScenarioComparison", "compare_scenarios"]

# Rolling resistance as fractions by surface type
_RR: dict[str, float] = {
    "asphalt": 0.015,
    "gravel": 0.040,
    "concrete": 0.012,
}

_DEFAULT_FUEL_PRICE_USD_PER_LITRE: float = 0.80
_DEFAULT_WORKING_DAYS_PER_YEAR: int = 250


class RoadScenario(BaseModel):
    """Simplified road scenario for cross-surface cost comparison."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    surface: Literal["asphalt", "gravel", "concrete"]
    thickness_mm: float = Field(ge=0, description="Pavement design thickness [mm]")
    haul_distance_km: float = Field(gt=0, description="One-way haul distance [km]")
    trips_per_day: float = Field(gt=0, description="One-way vehicle trips per day")


class ScenarioComparison(BaseModel):
    """Annual operating cost breakdown for one road scenario."""

    model_config = ConfigDict(frozen=True)

    name: str
    tire_cost_usd_per_year: float = Field(ge=0)
    fuel_cost_usd_per_year: float = Field(ge=0)
    maintenance_cost_usd_per_year: float = Field(ge=0)
    confidence: ConfidenceLabel = "experimental"


class ComparisonResult(BaseModel):
    """Ordered list of scenario cost comparisons."""

    model_config = ConfigDict(frozen=True)

    scenarios: list[ScenarioComparison]
    method: str = "haulpave-economics-rr-v1"
    confidence: ConfidenceLabel = "experimental"


def compare_scenarios(
    scenarios: list[RoadScenario],
    fuel_price_usd_per_litre: float = _DEFAULT_FUEL_PRICE_USD_PER_LITRE,
    working_days_per_year: int = _DEFAULT_WORKING_DAYS_PER_YEAR,
) -> ComparisonResult:
    """Compare annual operating costs across road surface scenarios.

    Parameters
    ----------
    scenarios:
        List of ``RoadScenario`` items to compare.  Order is preserved in
        the output.
    fuel_price_usd_per_litre:
        Fuel price [USD/L] (default 0.80 USD/L).
    working_days_per_year:
        Operating days per year used for annualisation (default 250).

    Returns
    -------
    ComparisonResult
        One :class:`ScenarioComparison` per input scenario, in the same order.

    Raises
    ------
    ValueError
        If ``working_days_per_year`` ≤ 0.
    """
    if working_days_per_year <= 0:
        raise ValueError(f"working_days_per_year must be > 0, got {working_days_per_year}")
    if fuel_price_usd_per_litre <= 0:
        raise ValueError(f"fuel_price_usd_per_litre must be > 0, got {fuel_price_usd_per_litre}")

    comparisons: list[ScenarioComparison] = []
    for s in scenarios:
        rr = _RR[s.surface]
        fuel_l_per_km = 2.042 + 29.2 * rr
        tyre_usd_per_km = 0.128 + 92.8 * rr
        maint_usd_per_km = 0.144 + 30.4 * rr

        km_per_year = s.haul_distance_km * s.trips_per_day * working_days_per_year

        comparisons.append(
            ScenarioComparison(
                name=s.name,
                fuel_cost_usd_per_year=fuel_l_per_km * fuel_price_usd_per_litre * km_per_year,
                tire_cost_usd_per_year=tyre_usd_per_km * km_per_year,
                maintenance_cost_usd_per_year=maint_usd_per_km * km_per_year,
            )
        )

    return ComparisonResult(scenarios=comparisons)
