"""Vehicle registry — canonical specs for mining haul trucks.

Returns a catalogue of :class:`VehicleEntry` records — lightweight summaries
suitable for UI selection lists and for seeding bridge scenarios.  Each entry
carries full axle-load data so callers can feed the CESA / coverages engines
without an extra lookup.

Axle loads use a 25 % front / 75 % rear gross-weight split, consistent with
CAT Performance Handbook Edition 47 (typical loaded-condition distribution).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec

__all__ = ["VehicleEntry", "find_by_id", "list_all"]


class VehicleEntry(BaseModel):
    """Lightweight vehicle registry record for UI / RPC payloads."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1, description="Unique vehicle identifier slug")
    name: str = Field(min_length=1, description="Vehicle display name")
    gvw_kn: float = Field(gt=0, description="Gross vehicle weight at rated payload [kN]")
    axles: int = Field(ge=1, description="Number of axle groups")
    vehicle: MiningVehicle = Field(description="Full specification for engine use")


# Standard OTR tyre spec for 57-inch class tyres (Bridgestone VMTL / Michelin XDR3)
_OTR_TIRE = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=50_000.0)


def _make_truck(
    id: str,
    name: str,
    gvw_kn: float,
    source: str,
) -> VehicleEntry:
    """Build a standard 2-axle-group haul truck entry.

    Axle load split: 25 % front single / 75 % rear tandem.
    Front: single axle (1 axle, 2 tyres).
    Rear:  tandem group (2 axles, 4 tyres per axle — dual tyres).
    """
    front_kn = round(gvw_kn * 0.25, 1)
    rear_kn = round(gvw_kn * 0.75, 1)
    mv = MiningVehicle(
        name=name,
        gross_vehicle_mass_t=round(gvw_kn / 9.81, 1),
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=front_kn, tire_spec=_OTR_TIRE),
            AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=rear_kn, tire_spec=_OTR_TIRE),
        ],
        source=source,
    )
    return VehicleEntry(id=id, name=name, gvw_kn=gvw_kn, axles=2, vehicle=mv)


# ---------------------------------------------------------------------------
# Registry — loaded GVW from OEM datasheets (GVW = empty weight + rated payload)
# ---------------------------------------------------------------------------
_SOURCE_CAT_PHB47 = "Caterpillar Performance Handbook Edition 47 (2017)"
_SOURCE_KOM_SS = "Komatsu Mining Product Specifications, 960E-1K (2018)"

_REGISTRY: list[VehicleEntry] = [
    # CAT 797F: empty 259.3 t + payload 363.0 t = 622.3 t → 6,104 kN
    _make_truck(
        id="cat-797f",
        name="Caterpillar 797F",
        gvw_kn=6_104.0,
        source=_SOURCE_CAT_PHB47,
    ),
    # CAT 789D: empty 155.2 t + payload 181.6 t = 336.8 t → 3,304 kN
    _make_truck(
        id="cat-789d",
        name="Caterpillar 789D",
        gvw_kn=3_304.0,
        source=_SOURCE_CAT_PHB47,
    ),
    # Komatsu 960E-1K: empty 277.0 t + payload 327.0 t = 604.0 t → 5,925 kN
    _make_truck(
        id="kom-960e",
        name="Komatsu 960E",
        gvw_kn=5_925.0,
        source=_SOURCE_KOM_SS,
    ),
    # CAT 785D: empty 133.1 t + payload 136.1 t = 269.2 t → 2,641 kN
    _make_truck(
        id="cat-785d",
        name="Caterpillar 785D",
        gvw_kn=2_641.0,
        source=_SOURCE_CAT_PHB47,
    ),
]

# Index for O(1) by-id lookup
_BY_ID: dict[str, VehicleEntry] = {entry.id: entry for entry in _REGISTRY}


def list_all() -> list[VehicleEntry]:
    """Return all registered vehicle entries."""
    return list(_REGISTRY)


def find_by_id(vehicle_id: str) -> VehicleEntry | None:
    """Return the registry entry for *vehicle_id*, or ``None`` if not found."""
    return _BY_ID.get(vehicle_id)
