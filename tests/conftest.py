"""Shared pytest fixtures for HaulPave test suite.

Provides reusable vehicle, fleet, and assertion helpers
used across unit tests and benchmark tests.
"""

from __future__ import annotations

import pytest

from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec

# --- Tire fixtures ---


@pytest.fixture()
def tire_heavy() -> TireSpec:
    """Heavy haul truck tire — high contact pressure."""
    return TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=5200.0)


@pytest.fixture()
def tire_standard() -> TireSpec:
    """Standard truck tire."""
    return TireSpec(contact_pressure_kpa=550.0, contact_area_mm2=4500.0)


# --- Vehicle fixtures ---


@pytest.fixture()
def vehicle_cat_793f() -> MiningVehicle:
    """CAT 793F — 385t payload haul truck (heavy fleet design vehicle).

    Source: Caterpillar 793F spec sheet, 2023.
    Front: single axle 550kN, 2 tires.
    Rear: tandem group 1900kN, 4 tires per axle × 2 axles = 8 tires.
    """
    tire = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=5200.0)
    return MiningVehicle(
        name="CAT 793F",
        gross_vehicle_mass_t=623.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=550.0, tire_spec=tire),
            AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=1900.0, tire_spec=tire),
        ],
        source="Caterpillar 793F spec sheet, 2023",
    )


@pytest.fixture()
def vehicle_cat_785d() -> MiningVehicle:
    """CAT 785D — 150t payload haul truck (medium fleet).

    Source: Caterpillar 785D spec sheet, 2023.
    """
    tire = TireSpec(contact_pressure_kpa=620.0, contact_area_mm2=4800.0)
    return MiningVehicle(
        name="CAT 785D",
        gross_vehicle_mass_t=269.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=225.0, tire_spec=tire),
            AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=1040.0, tire_spec=tire),
        ],
        source="Caterpillar 785D spec sheet, 2023",
    )


@pytest.fixture()
def vehicle_cat_777g() -> MiningVehicle:
    """CAT 777G — 90t payload haul truck (light fleet).

    Source: Caterpillar 777G spec sheet, 2023.
    """
    tire = TireSpec(contact_pressure_kpa=550.0, contact_area_mm2=4200.0)
    return MiningVehicle(
        name="CAT 777G",
        gross_vehicle_mass_t=186.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=155.0, tire_spec=tire),
            AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=760.0, tire_spec=tire),
        ],
        source="Caterpillar 777G spec sheet, 2023",
    )


# --- Fleet fixtures ---


@pytest.fixture()
def fleet_heavy(vehicle_cat_793f: MiningVehicle) -> list[FleetUnit]:
    """Heavy fleet: CAT 793F + fuel truck."""
    fuel_tire = TireSpec(contact_pressure_kpa=480.0, contact_area_mm2=3800.0)
    fuel_truck = MiningVehicle(
        name="Fuel truck",
        gross_vehicle_mass_t=30.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=100.0, tire_spec=fuel_tire),
            AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=200.0, tire_spec=fuel_tire),
        ],
        source="Generic fuel truck spec",
    )
    return [
        FleetUnit(vehicle=vehicle_cat_793f, trips_per_day=30.0),
        FleetUnit(vehicle=fuel_truck, trips_per_day=15.0),
    ]


@pytest.fixture()
def fleet_medium(vehicle_cat_785d: MiningVehicle) -> list[FleetUnit]:
    """Medium fleet: CAT 785D + motor grader."""
    grader_tire = TireSpec(contact_pressure_kpa=380.0, contact_area_mm2=3200.0)
    grader = MiningVehicle(
        name="Motor grader",
        gross_vehicle_mass_t=25.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=85.0, tire_spec=grader_tire),
            AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=160.0, tire_spec=grader_tire),
        ],
        source="Generic motor grader spec",
    )
    return [
        FleetUnit(vehicle=vehicle_cat_785d, trips_per_day=40.0),
        FleetUnit(vehicle=grader, trips_per_day=5.0),
    ]


@pytest.fixture()
def fleet_light(vehicle_cat_777g: MiningVehicle) -> list[FleetUnit]:
    """Light fleet: CAT 777G + water truck."""
    water_tire = TireSpec(contact_pressure_kpa=420.0, contact_area_mm2=3600.0)
    water_truck = MiningVehicle(
        name="Water truck",
        gross_vehicle_mass_t=40.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=120.0, tire_spec=water_tire),
            AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=270.0, tire_spec=water_tire),
        ],
        source="Generic water truck spec",
    )
    return [
        FleetUnit(vehicle=vehicle_cat_777g, trips_per_day=50.0),
        FleetUnit(vehicle=water_truck, trips_per_day=10.0),
    ]


# --- Shared test helpers (plain functions — not fixtures, because they take parameters) ---

PLACEHOLDER_TIRE = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=50000.0)


def make_single_axle(load_kn: float) -> AxleGroup:
    """Single axle: 1 axle, 2 tyres per axle."""
    return AxleGroup(
        axle_count=1,
        tyres_per_axle=2,
        gross_load_kn=load_kn,
        tire_spec=PLACEHOLDER_TIRE,
    )


def make_tandem_axle(load_kn: float) -> AxleGroup:
    """Tandem axle group: 2 axles, 4 tyres per axle (dual-tyre stations)."""
    return AxleGroup(
        axle_count=2,
        tyres_per_axle=4,
        gross_load_kn=load_kn,
        tire_spec=PLACEHOLDER_TIRE,
    )


def make_tridem_axle(load_kn: float) -> AxleGroup:
    """Tridem axle group: 3 axles, 4 tyres per axle."""
    return AxleGroup(
        axle_count=3,
        tyres_per_axle=4,
        gross_load_kn=load_kn,
        tire_spec=PLACEHOLDER_TIRE,
    )


def make_vehicle(
    name: str,
    axle_groups: list[AxleGroup],
    gvm_t: float = 50.0,
) -> MiningVehicle:
    """Create a MiningVehicle with a synthetic source string."""
    return MiningVehicle(
        name=name,
        gross_vehicle_mass_t=gvm_t,
        axle_groups=axle_groups,
        source="Synthetic vehicle for unit tests",
    )


def make_traffic(
    vehicle: MiningVehicle,
    trips: float = 10,
    life_years: float = 10,
    days_per_year: int = 350,
) -> TrafficInput:
    """Create a TrafficInput with a single-vehicle fleet."""
    return TrafficInput(
        fleet=[FleetUnit(vehicle=vehicle, trips_per_day=trips)],
        design_life_years=life_years,
        working_days_per_year=days_per_year,
    )


# --- Assertion helpers ---


def assert_within_pct(actual: float, expected: float, tolerance_pct: float) -> None:
    """Assert that actual is within tolerance_pct of expected."""
    if expected == 0:
        assert actual == 0, f"Expected 0, got {actual}"
        return
    error_pct = abs(actual - expected) / abs(expected) * 100
    assert error_pct <= tolerance_pct, (
        f"Value {actual:.4g} is {error_pct:.2f}% from expected {expected:.4g} "
        f"(tolerance: {tolerance_pct}%)"
    )
