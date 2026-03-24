"""Vehicle data models — TireSpec, AxleGroup, MiningVehicle.

All dimensional fields use SI units: forces in kN, masses in tonnes.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TireSpec(BaseModel):
    """Specification for a single tire."""

    model_config = ConfigDict(frozen=True)

    contact_pressure_kpa: float = Field(gt=0, description="Tyre contact pressure [kPa]")
    contact_area_mm2: float = Field(gt=0, description="Tyre contact area [mm²]")


class AxleGroup(BaseModel):
    """An axle group (single, tandem, or tridem)."""

    model_config = ConfigDict(frozen=True)

    axle_count: int = Field(ge=1, le=4, description="Number of axles in group")
    tyres_per_axle: int = Field(ge=2, description="Tyres per axle")
    gross_load_kn: float = Field(gt=0, description="Total load on axle group [kN]")
    tire_spec: TireSpec


class MiningVehicle(BaseModel):
    """Mining haul truck or ancillary equipment — fully specified for pavement design.

    The ``source`` field is mandatory: all vehicle data must be traceable to a
    published spec sheet or OEM datasheet (no implicit assumptions).
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, description="Vehicle make/model identifier")
    gross_vehicle_mass_t: float = Field(gt=0, description="Gross vehicle mass [tonnes]")
    axle_groups: list[AxleGroup] = Field(min_length=1)
    source: str = Field(
        min_length=1,
        description="Mandatory provenance — OEM spec sheet, report, or datasheet reference",
    )

    @field_validator("axle_groups")
    @classmethod
    def at_least_one_axle_group(cls, v: list[AxleGroup]) -> list[AxleGroup]:
        if not v:
            raise ValueError("MiningVehicle must have at least one axle group")
        return v
