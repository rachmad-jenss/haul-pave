"""Unit tests for haulpave.traffic.coverages.

Tests the USACE TM 5-822-12 pass-count method implementation including:
- CoveragesResult dataclass structure and defaults
- Wheel load calculation for single and tandem axle groups
- Wheel position counting
- Design wheel load selection (max across fleet)
- Total coverages calculation
- Edge cases: single vehicle, single axle group
"""

from __future__ import annotations

import math

import pytest

from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.models.vehicle import AxleGroup, MiningVehicle
from haulpave.traffic.coverages import (
    CoveragesResult,
    _design_wheel_load_kn,
    _equiv_passes_per_day,
    _wheel_load_kn,
    _wheel_positions,
    compute_coverages,
)

from ..conftest import PLACEHOLDER_TIRE, make_single_axle, make_tandem_axle


def _make_vehicle(
    name: str,
    gvm_t: float,
    axle_groups: list[AxleGroup],
) -> MiningVehicle:
    return MiningVehicle(
        name=name,
        gross_vehicle_mass_t=gvm_t,
        axle_groups=axle_groups,
        source="Synthetic test vehicle",
    )


def _make_traffic(
    fleet: list[FleetUnit],
    design_life: float = 10.0,
    working_days: int = 350,
) -> TrafficInput:
    return TrafficInput(
        fleet=fleet,
        design_life_years=design_life,
        working_days_per_year=working_days,
    )


# ---------------------------------------------------------------------------
# CoveragesResult dataclass
# ---------------------------------------------------------------------------


class TestCoveragesResult:
    def test_frozen(self) -> None:
        result = CoveragesResult(total_coverages=1000.0, design_wheel_load_kn=77.5)
        with pytest.raises((AttributeError, TypeError)):
            result.total_coverages = 999.0  # type: ignore[misc]

    def test_default_method_contains_usace(self) -> None:
        result = CoveragesResult(total_coverages=1000.0, design_wheel_load_kn=77.5)
        assert "USACE" in result.method

    def test_default_confidence(self) -> None:
        result = CoveragesResult(total_coverages=1000.0, design_wheel_load_kn=77.5)
        assert result.confidence == "high"

    def test_fields_accessible(self) -> None:
        result = CoveragesResult(total_coverages=12345.6, design_wheel_load_kn=112.5)
        assert result.total_coverages == 12345.6
        assert result.design_wheel_load_kn == 112.5


# ---------------------------------------------------------------------------
# _wheel_load_kn
# ---------------------------------------------------------------------------


class TestWheelLoadKn:
    def test_single_axle_2tyres(self) -> None:
        """Single axle, 2 tyres, 155 kN → 77.5 kN/wheel."""
        group = make_single_axle(155.0)
        assert math.isclose(_wheel_load_kn(group), 77.5, rel_tol=1e-9)

    def test_single_axle_120kn(self) -> None:
        """Single axle, 2 tyres, 120 kN → 60.0 kN/wheel."""
        group = make_single_axle(120.0)
        assert math.isclose(_wheel_load_kn(group), 60.0, rel_tol=1e-9)

    def test_tandem_axle_760kn(self) -> None:
        """Tandem: 2 axles, 4 tyres/axle, 760 kN → 760/16 = 47.5 kN/wheel."""
        group = make_tandem_axle(760.0)
        assert math.isclose(_wheel_load_kn(group), 47.5, rel_tol=1e-9)

    def test_tandem_axle_1040kn(self) -> None:
        """Tandem: 2 axles, 4 tyres/axle, 1040 kN → 1040/16 = 65.0 kN/wheel."""
        group = make_tandem_axle(1040.0)
        assert math.isclose(_wheel_load_kn(group), 65.0, rel_tol=1e-9)

    def test_tandem_axle_1900kn(self) -> None:
        """Tandem: 2 axles, 4 tyres/axle, 1900 kN → 1900/16 = 118.75 kN/wheel."""
        group = make_tandem_axle(1900.0)
        assert math.isclose(_wheel_load_kn(group), 118.75, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# _wheel_positions
# ---------------------------------------------------------------------------


class TestWheelPositions:
    def test_single_axle_is_1(self) -> None:
        group = make_single_axle(100.0)
        assert _wheel_positions(group) == 1

    def test_tandem_axle_is_8(self) -> None:
        """Tandem: axle_count=2 * tyres_per_axle=4 = 8 positions."""
        group = make_tandem_axle(100.0)
        assert _wheel_positions(group) == 8

    def test_tridem_axle(self) -> None:
        """Tridem (axle_count=3, tyres_per_axle=4): 3 * 4 = 12 positions."""
        group = AxleGroup(
            axle_count=3,
            tyres_per_axle=4,
            gross_load_kn=200.0,
            tire_spec=PLACEHOLDER_TIRE,
        )
        assert _wheel_positions(group) == 12


# ---------------------------------------------------------------------------
# _design_wheel_load_kn
# ---------------------------------------------------------------------------


class TestDesignWheelLoad:
    def test_single_vehicle_single_axle_design_wheel(self) -> None:
        vehicle = _make_vehicle("V1", 30.0, [make_single_axle(200.0)])
        traffic = _make_traffic([FleetUnit(vehicle=vehicle, trips_per_day=10)])
        assert math.isclose(_design_wheel_load_kn(traffic), 100.0, rel_tol=1e-9)

    def test_picks_max_across_axle_groups(self) -> None:
        """Front axle load (77.5) > rear tandem load (47.5): design = 77.5."""
        vehicle = _make_vehicle("V1", 186.0, [make_single_axle(155.0), make_tandem_axle(760.0)])  # noqa: E501
        traffic = _make_traffic([FleetUnit(vehicle=vehicle, trips_per_day=50)])
        assert math.isclose(_design_wheel_load_kn(traffic), 77.5, rel_tol=1e-9)

    def test_picks_max_across_fleet(self) -> None:
        """Design load comes from the heaviest vehicle in the fleet."""
        v1 = _make_vehicle("Light", 40.0, [make_single_axle(120.0)])
        v2 = _make_vehicle("Heavy", 186.0, [make_single_axle(155.0)])
        traffic = _make_traffic(
            [
                FleetUnit(vehicle=v1, trips_per_day=10),
                FleetUnit(vehicle=v2, trips_per_day=50),
            ]
        )
        assert math.isclose(_design_wheel_load_kn(traffic), 77.5, rel_tol=1e-9)

    def test_fleet_a_design_wheel_load(self) -> None:
        """Fleet A: 77.5 kN (CAT 777G front axle ÷ 2)."""
        cat_777g = _make_vehicle(
            "CAT 777G", 186.0, [make_single_axle(155.0), make_tandem_axle(760.0)]
        )  # noqa: E501
        water_truck = _make_vehicle(
            "Water Truck", 40.0, [make_single_axle(120.0), make_tandem_axle(270.0)]
        )  # noqa: E501
        traffic = _make_traffic(
            [
                FleetUnit(vehicle=cat_777g, trips_per_day=50),
                FleetUnit(vehicle=water_truck, trips_per_day=10),
            ]
        )
        assert math.isclose(_design_wheel_load_kn(traffic), 77.5, rel_tol=1e-4)


# ---------------------------------------------------------------------------
# _equiv_passes_per_day
# ---------------------------------------------------------------------------


class TestEquivPassesPerDay:
    def test_design_vehicle_contributes_positions_times_trips_times_2(self) -> None:
        """Design vehicle (wheel_load == design_wheel_load) contributes
        positions * trips_per_day * 2 equiv passes per day.
        Single axle: 1 position. 10 trips × 2 directions = 20 passes.
        """
        group = make_single_axle(200.0)
        design_wheel_load = 100.0  # 200/2 = 100 kN
        result = _equiv_passes_per_day(
            [group], trips_per_day=10, design_wheel_load=design_wheel_load
        )
        assert math.isclose(result, 20.0, rel_tol=1e-9)

    def test_half_load_single_axle_4th_power(self) -> None:
        """wheel_load = 50, design = 100 → ratio^4 = (0.5)^4 = 1/16.
        1 position × (0.5)^4 × 10 trips × 2 dirs = 20/16 = 1.25.
        """
        group = make_single_axle(100.0)  # wheel_load = 50
        result = _equiv_passes_per_day([group], trips_per_day=10, design_wheel_load=100.0)
        assert math.isclose(result, 20.0 / 16.0, rel_tol=1e-9)

    def test_cat_777g_front_contribution(self) -> None:
        """CAT 777G front axle: positions=1, wheel=77.5, design=77.5.
        ratio^4 = 1.0. trips=50 × 2 × 1 = 100.
        """
        group = make_single_axle(155.0)
        result = _equiv_passes_per_day([group], trips_per_day=50, design_wheel_load=77.5)
        assert math.isclose(result, 100.0, rel_tol=1e-6)

    def test_cat_777g_rear_contribution(self) -> None:
        """CAT 777G rear tandem: positions=8, wheel=47.5, design=77.5.
        ratio = 47.5/77.5. positions × ratio^4 × 50 × 2 = 8 × 0.141113 × 100 ≈ 112.89.
        """
        group = make_tandem_axle(760.0)
        result = _equiv_passes_per_day([group], trips_per_day=50, design_wheel_load=77.5)
        expected = 8 * (47.5 / 77.5) ** 4 * 50 * 2
        assert math.isclose(result, expected, rel_tol=1e-6)


# ---------------------------------------------------------------------------
# compute_coverages — main function
# ---------------------------------------------------------------------------


class TestComputeCoverages:
    def test_returns_coverages_result(self) -> None:
        vehicle = _make_vehicle("V1", 30.0, [make_single_axle(100.0)])
        traffic = _make_traffic([FleetUnit(vehicle=vehicle, trips_per_day=10)])
        result = compute_coverages(traffic)
        assert isinstance(result, CoveragesResult)

    def test_method_contains_usace(self) -> None:
        vehicle = _make_vehicle("V1", 30.0, [make_single_axle(100.0)])
        traffic = _make_traffic([FleetUnit(vehicle=vehicle, trips_per_day=10)])
        result = compute_coverages(traffic)
        assert "USACE" in result.method or "coverage" in result.method.lower()

    def test_single_vehicle_single_axle_coverages(self) -> None:
        """Single vehicle, single axle: design = vehicle wheel load.
        Ratio = 1.0, so coverages = trips × 2 × 1_position × working_days × years.
        """
        vehicle = _make_vehicle("V1", 30.0, [make_single_axle(200.0)])
        traffic = _make_traffic(
            [FleetUnit(vehicle=vehicle, trips_per_day=10)],
            design_life=5.0,
            working_days=300,
        )
        result = compute_coverages(traffic)
        expected = 10 * 2 * 1 * 300 * 5  # 30000
        assert math.isclose(result.total_coverages, expected, rel_tol=1e-9)
        assert math.isclose(result.design_wheel_load_kn, 100.0, rel_tol=1e-9)

    def test_fleet_a_total_coverages(self) -> None:
        """Fleet A hand-calc: 771,523.33 coverages (±2%)."""
        cat_777g = _make_vehicle(
            "CAT 777G", 186.0, [make_single_axle(155.0), make_tandem_axle(760.0)]
        )  # noqa: E501
        water_truck = _make_vehicle(
            "Water Truck", 40.0, [make_single_axle(120.0), make_tandem_axle(270.0)]
        )  # noqa: E501
        traffic = _make_traffic(
            [
                FleetUnit(vehicle=cat_777g, trips_per_day=50),
                FleetUnit(vehicle=water_truck, trips_per_day=10),
            ]
        )
        result = compute_coverages(traffic)
        expected = 771523.33
        rel_err = abs(result.total_coverages - expected) / expected
        assert rel_err <= 0.02, (
            f"Fleet A: computed={result.total_coverages:.2f}, "
            f"expected={expected:.2f}, rel_err={rel_err:.4%}"
        )

    def test_fleet_b_total_coverages(self) -> None:
        """Fleet B hand-calc: 530,357.24 coverages (±2%)."""
        cat_785d = _make_vehicle(
            "CAT 785D", 269.0, [make_single_axle(225.0), make_tandem_axle(1040.0)]
        )  # noqa: E501
        motor_grader = _make_vehicle(
            "Motor Grader", 25.0, [make_single_axle(85.0), make_tandem_axle(160.0)]
        )
        traffic = _make_traffic(
            [
                FleetUnit(vehicle=cat_785d, trips_per_day=40),
                FleetUnit(vehicle=motor_grader, trips_per_day=5),
            ]
        )
        result = compute_coverages(traffic)
        expected = 530357.24
        rel_err = abs(result.total_coverages - expected) / expected
        assert rel_err <= 0.02, (
            f"Fleet B: computed={result.total_coverages:.2f}, "
            f"expected={expected:.2f}, rel_err={rel_err:.4%}"
        )

    def test_fleet_c_total_coverages(self) -> None:
        """Fleet C hand-calc: 268,531.80 coverages (±2%)."""
        cat_793f = _make_vehicle(
            "CAT 793F", 623.0, [make_single_axle(550.0), make_tandem_axle(1900.0)]
        )  # noqa: E501
        fuel_truck = _make_vehicle(
            "Fuel Truck", 30.0, [make_single_axle(100.0), make_tandem_axle(200.0)]
        )  # noqa: E501
        traffic = _make_traffic(
            [
                FleetUnit(vehicle=cat_793f, trips_per_day=30),
                FleetUnit(vehicle=fuel_truck, trips_per_day=15),
            ]
        )
        result = compute_coverages(traffic)
        expected = 268531.80
        rel_err = abs(result.total_coverages - expected) / expected
        assert rel_err <= 0.02, (
            f"Fleet C: computed={result.total_coverages:.2f}, "
            f"expected={expected:.2f}, rel_err={rel_err:.4%}"
        )

    def test_design_wheel_load_fleet_a(self) -> None:
        """Fleet A design wheel load: 77.5 kN."""
        cat_777g = _make_vehicle(
            "CAT 777G", 186.0, [make_single_axle(155.0), make_tandem_axle(760.0)]
        )  # noqa: E501
        water_truck = _make_vehicle(
            "Water Truck", 40.0, [make_single_axle(120.0), make_tandem_axle(270.0)]
        )  # noqa: E501
        traffic = _make_traffic(
            [
                FleetUnit(vehicle=cat_777g, trips_per_day=50),
                FleetUnit(vehicle=water_truck, trips_per_day=10),
            ]
        )
        result = compute_coverages(traffic)
        assert math.isclose(result.design_wheel_load_kn, 77.5, rel_tol=1e-4)

    def test_coverages_scale_linearly_with_trips(self) -> None:
        """Doubling trips_per_day doubles total_coverages."""
        vehicle = _make_vehicle("V1", 30.0, [make_single_axle(200.0)])
        t1 = _make_traffic([FleetUnit(vehicle=vehicle, trips_per_day=10)])
        t2 = _make_traffic([FleetUnit(vehicle=vehicle, trips_per_day=20)])
        r1 = compute_coverages(t1)
        r2 = compute_coverages(t2)
        assert math.isclose(r2.total_coverages / r1.total_coverages, 2.0, rel_tol=1e-9)

    def test_coverages_scale_linearly_with_design_life(self) -> None:
        """Doubling design_life_years doubles total_coverages."""
        vehicle = _make_vehicle("V1", 30.0, [make_single_axle(200.0)])
        t1 = _make_traffic([FleetUnit(vehicle=vehicle, trips_per_day=10)], design_life=5.0)
        t2 = _make_traffic([FleetUnit(vehicle=vehicle, trips_per_day=10)], design_life=10.0)
        r1 = compute_coverages(t1)
        r2 = compute_coverages(t2)
        assert math.isclose(r2.total_coverages / r1.total_coverages, 2.0, rel_tol=1e-9)

    def test_fourth_power_weighting(self) -> None:
        """Half wheel load → coverage contribution reduced by factor 16 (0.5^4)."""
        design_vehicle = _make_vehicle("Design", 30.0, [make_single_axle(200.0)])
        light_vehicle = _make_vehicle("Light", 15.0, [make_single_axle(100.0)])

        t_design = _make_traffic([FleetUnit(vehicle=design_vehicle, trips_per_day=10)])
        t_mixed = _make_traffic(
            [
                FleetUnit(vehicle=design_vehicle, trips_per_day=10),
                FleetUnit(vehicle=light_vehicle, trips_per_day=10),
            ]
        )
        r_design = compute_coverages(t_design)
        r_mixed = compute_coverages(t_mixed)
        expected_ratio = 1.0 + (0.5**4)  # 1.0625
        actual_ratio = r_mixed.total_coverages / r_design.total_coverages
        assert math.isclose(actual_ratio, expected_ratio, rel_tol=1e-5), (
            f"Expected ratio {expected_ratio:.6f}, got {actual_ratio:.6f}"
        )

    def test_confidence_is_high(self) -> None:
        vehicle = _make_vehicle("V1", 30.0, [make_single_axle(100.0)])
        traffic = _make_traffic([FleetUnit(vehicle=vehicle, trips_per_day=10)])
        result = compute_coverages(traffic)
        assert result.confidence == "high"

    def test_positive_coverages(self) -> None:
        vehicle = _make_vehicle("V1", 30.0, [make_single_axle(100.0)])
        traffic = _make_traffic([FleetUnit(vehicle=vehicle, trips_per_day=5)])
        result = compute_coverages(traffic)
        assert result.total_coverages > 0
