"""Economics data models — CostAssumptions, CostScenario, EconomicResult.

All monetary values in USD (or consistent user currency — no mixing).
Distance in km, mass in tonnes, fuel in L.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CostAssumptions(BaseModel):
    """Unit cost assumptions for haul road operating cost analysis."""

    model_config = ConfigDict(frozen=True)

    fuel_cost_per_litre: float = Field(gt=0, description="Fuel price [currency/L]")
    tyre_cost_per_hour: float = Field(ge=0, description="Tyre wear cost [currency/hr]")
    maintenance_cost_per_km: float = Field(ge=0, description="Maintenance cost [currency/km]")
    operator_cost_per_hour: float = Field(ge=0, description="Operator cost [currency/hr]")
    currency: str = Field(
        default="USD",
        description="ISO 4217 currency code",
        min_length=3,
        max_length=3,
        pattern=r"^[A-Z]{3}$",
    )


class CostScenario(BaseModel):
    """A single operating cost scenario — one road geometry + one fleet + one cost set."""

    model_config = ConfigDict(frozen=True)

    scenario_id: str = Field(min_length=1)
    haul_distance_km: float = Field(gt=0, description="One-way haul distance [km]")
    average_speed_kmh: float = Field(gt=0, description="Average laden speed [km/h]")
    payload_t: float = Field(gt=0, description="Payload per trip [tonnes]")
    fuel_consumption_l_per_km: float = Field(gt=0, description="Fuel consumption [L/km]")
    assumptions: CostAssumptions


class EconomicResult(BaseModel):
    """Operating cost analysis output for a scenario."""

    model_config = ConfigDict(frozen=True)

    scenario_id: str = Field(min_length=1)
    cost_per_tonne_km: float = Field(ge=0, description="Unit transport cost [currency/t·km]")
    cost_per_trip: float = Field(ge=0, description="Total cost per one-way trip [currency]")
    trips_per_year: float = Field(ge=0, description="Annual trip count")
    annual_cost: float = Field(ge=0, description="Annual operating cost [currency]")
    currency: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    method: str = Field(default="haulpave-economics-v1", description="Calculation method ID")
