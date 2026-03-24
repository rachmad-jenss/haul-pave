"""Traffic data models — FleetUnit, HaulSegment, TrafficInput, TrafficResult.

All distance fields in km, mass in tonnes.
"""

from __future__ import annotations

import warnings

from pydantic import BaseModel, ConfigDict, Field, model_validator

from haulpave.models.vehicle import MiningVehicle


class FleetUnit(BaseModel):
    """A vehicle type with its daily trip count."""

    model_config = ConfigDict(frozen=True)

    vehicle: MiningVehicle
    trips_per_day: float = Field(gt=0, description="One-way trips per day")


class HaulSegment(BaseModel):
    """A road segment with its own fleet mix.

    .. warning::
        This model is **experimental**. The multi-segment traffic accumulation
        method has not been benchmark-tested against a published hand-calculation.
        Use with caution and validate outputs independently.
    """

    model_config = ConfigDict(frozen=True)

    segment_id: str = Field(min_length=1)
    length_km: float = Field(gt=0, description="Segment length [km]")
    fleet: list[FleetUnit] = Field(min_length=1)

    def __init__(self, **data: object) -> None:
        super().__init__(**data)
        warnings.warn(
            "HaulSegment is experimental and has not been benchmark-tested. "
            "Validate outputs independently.",
            UserWarning,
            stacklevel=2,
        )


class TrafficInput(BaseModel):
    """Traffic loading inputs for a single design section."""

    model_config = ConfigDict(frozen=True)

    fleet: list[FleetUnit] = Field(min_length=1, description="Fleet mix for this section")
    design_life_years: float = Field(gt=0, description="Pavement design life [years]")
    working_days_per_year: int = Field(
        gt=0, le=366, description="Operating days per year", default=250
    )

    @model_validator(mode="after")
    def fleet_must_be_non_empty(self) -> TrafficInput:
        if not self.fleet:
            raise ValueError("TrafficInput.fleet must contain at least one FleetUnit")
        return self


class TrafficResult(BaseModel):
    """Computed traffic loading output."""

    model_config = ConfigDict(frozen=True)

    total_coverages: float = Field(ge=0, description="Equivalent design coverages")
    total_esal: float = Field(ge=0, description="Equivalent single-axle loads (AASHTO)")
    design_life_years: float = Field(gt=0)
    method: str = Field(default="USACE TM 5-822-12", description="Calculation method ID")
