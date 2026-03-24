"""Tests for haulpave.models.vehicle."""

import pytest
from pydantic import ValidationError

from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec


@pytest.fixture()
def tire() -> TireSpec:
    return TireSpec(contact_pressure_kpa=550.0, contact_area_mm2=4500.0)


@pytest.fixture()
def axle(tire: TireSpec) -> AxleGroup:
    return AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=320.0, tire_spec=tire)


@pytest.fixture()
def vehicle(axle: AxleGroup) -> MiningVehicle:
    return MiningVehicle(
        name="CAT 793F",
        gross_vehicle_mass_t=385.0,
        axle_groups=[axle],
        source="Caterpillar 793F spec sheet, 2023",
    )


class TestTireSpec:
    def test_valid(self, tire: TireSpec) -> None:
        assert tire.contact_pressure_kpa == 550.0
        assert tire.contact_area_mm2 == 4500.0

    def test_zero_pressure_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TireSpec(contact_pressure_kpa=0, contact_area_mm2=4500.0)

    def test_negative_area_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TireSpec(contact_pressure_kpa=550.0, contact_area_mm2=-1.0)

    def test_immutable(self, tire: TireSpec) -> None:
        with pytest.raises(ValidationError):
            tire.contact_pressure_kpa = 100.0  # type: ignore[misc]


class TestAxleGroup:
    def test_valid(self, axle: AxleGroup) -> None:
        assert axle.axle_count == 2
        assert axle.gross_load_kn == 320.0

    def test_too_many_axles_rejected(self, tire: TireSpec) -> None:
        with pytest.raises(ValidationError):
            AxleGroup(axle_count=5, tyres_per_axle=4, gross_load_kn=100.0, tire_spec=tire)

    def test_zero_load_rejected(self, tire: TireSpec) -> None:
        with pytest.raises(ValidationError):
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=0.0, tire_spec=tire)


class TestMiningVehicle:
    def test_valid(self, vehicle: MiningVehicle) -> None:
        assert vehicle.name == "CAT 793F"
        assert vehicle.gross_vehicle_mass_t == 385.0
        assert vehicle.source == "Caterpillar 793F spec sheet, 2023"

    def test_source_required(self, axle: AxleGroup) -> None:
        with pytest.raises(ValidationError):
            MiningVehicle(name="X", gross_vehicle_mass_t=100.0, axle_groups=[axle], source="")

    def test_empty_axle_groups_rejected(self) -> None:
        with pytest.raises(ValidationError):
            MiningVehicle(name="X", gross_vehicle_mass_t=100.0, axle_groups=[], source="test")

    def test_immutable(self, vehicle: MiningVehicle) -> None:
        with pytest.raises(ValidationError):
            vehicle.name = "Other"  # type: ignore[misc]
