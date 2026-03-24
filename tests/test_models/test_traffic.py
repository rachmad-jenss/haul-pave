"""Tests for haulpave.models.traffic."""

import warnings

import pytest
from pydantic import ValidationError

from haulpave.models.traffic import FleetUnit, HaulSegment, TrafficInput, TrafficResult
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec


@pytest.fixture()
def vehicle() -> MiningVehicle:
    tire = TireSpec(contact_pressure_kpa=550.0, contact_area_mm2=4500.0)
    axle = AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=320.0, tire_spec=tire)
    return MiningVehicle(
        name="CAT 793F",
        gross_vehicle_mass_t=385.0,
        axle_groups=[axle],
        source="CAT spec 2023",
    )


@pytest.fixture()
def fleet_unit(vehicle: MiningVehicle) -> FleetUnit:
    return FleetUnit(vehicle=vehicle, trips_per_day=20.0)


class TestFleetUnit:
    def test_valid(self, fleet_unit: FleetUnit) -> None:
        assert fleet_unit.trips_per_day == 20.0

    def test_zero_trips_rejected(self, vehicle: MiningVehicle) -> None:
        with pytest.raises(ValidationError):
            FleetUnit(vehicle=vehicle, trips_per_day=0.0)


class TestHaulSegment:
    def test_warns_experimental(self, fleet_unit: FleetUnit) -> None:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            HaulSegment(segment_id="S1", length_km=5.0, fleet=[fleet_unit])
            assert len(w) == 1
            assert issubclass(w[0].category, UserWarning)
            assert "experimental" in str(w[0].message).lower()

    def test_valid(self, fleet_unit: FleetUnit) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            seg = HaulSegment(segment_id="S1", length_km=5.0, fleet=[fleet_unit])
        assert seg.length_km == 5.0

    def test_zero_length_rejected(self, fleet_unit: FleetUnit) -> None:
        with pytest.raises(ValidationError):
            HaulSegment(segment_id="S1", length_km=0.0, fleet=[fleet_unit])

    def test_invalid_data_emits_no_warning(self, fleet_unit: FleetUnit) -> None:
        with warnings.catch_warnings(record=True) as w, pytest.raises(ValidationError):
            warnings.simplefilter("always")
            HaulSegment(segment_id="S1", length_km=0.0, fleet=[fleet_unit])
        assert len(w) == 0


class TestTrafficInput:
    def test_valid(self, fleet_unit: FleetUnit) -> None:
        ti = TrafficInput(fleet=[fleet_unit], design_life_years=10.0)
        assert ti.working_days_per_year == 250

    def test_empty_fleet_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TrafficInput(fleet=[], design_life_years=10.0)

    def test_zero_life_rejected(self, fleet_unit: FleetUnit) -> None:
        with pytest.raises(ValidationError):
            TrafficInput(fleet=[fleet_unit], design_life_years=0.0)


class TestTrafficResult:
    def test_valid(self) -> None:
        tr = TrafficResult(
            total_coverages=1500.0,
            total_esal=2000.0,
            design_life_years=10.0,
        )
        assert tr.method == "USACE TM 5-822-12"

    def test_negative_coverages_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TrafficResult(total_coverages=-1.0, total_esal=100.0, design_life_years=10.0)
