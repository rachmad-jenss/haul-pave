"""Unit tests for haulpave.traffic.cesa — AASHTO 4th-power CESA engine."""

from __future__ import annotations

import math

import pytest

from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec
from haulpave.traffic.cesa import CesaResult, _lef_for_axle_group, compute_cesa

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TIRE = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=50000.0)


def _single(load_kn: float) -> AxleGroup:
    """Single axle (axle_count=1)."""
    return AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=load_kn, tire_spec=_TIRE)


def _tandem(load_kn: float) -> AxleGroup:
    """Tandem axle group (axle_count=2)."""
    return AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=load_kn, tire_spec=_TIRE)


def _tridem(load_kn: float) -> AxleGroup:
    """Tridem axle group (axle_count=3)."""
    return AxleGroup(axle_count=3, tyres_per_axle=4, gross_load_kn=load_kn, tire_spec=_TIRE)


def _make_vehicle(name: str, axle_groups: list[AxleGroup]) -> MiningVehicle:
    return MiningVehicle(
        name=name,
        gross_vehicle_mass_t=50.0,
        axle_groups=axle_groups,
        source="Synthetic vehicle for unit tests",
    )


def _make_traffic(
    vehicle: MiningVehicle,
    trips: float = 10,
    life_years: float = 10,
    days_per_year: int = 350,
) -> TrafficInput:
    return TrafficInput(
        fleet=[FleetUnit(vehicle=vehicle, trips_per_day=trips)],
        design_life_years=life_years,
        working_days_per_year=days_per_year,
    )


# ---------------------------------------------------------------------------
# Tests: _lef_for_axle_group
# ---------------------------------------------------------------------------


class TestLefForAxleGroup:
    """Unit tests for the LEF helper function."""

    def test_standard_single_axle_lef_is_one(self) -> None:
        """Standard single axle (80 kN) must give LEF = 1.0."""
        group = _single(80.0)
        assert math.isclose(_lef_for_axle_group(group), 1.0, rel_tol=1e-9)

    def test_standard_tandem_lef_is_two(self) -> None:
        """Standard tandem (160 kN total) must give LEF = 2.0."""
        group = _tandem(160.0)
        assert math.isclose(_lef_for_axle_group(group), 2.0, rel_tol=1e-9)

    def test_standard_tridem_lef_is_three(self) -> None:
        """Standard tridem (240 kN total) must give LEF = 3.0."""
        group = _tridem(240.0)
        assert math.isclose(_lef_for_axle_group(group), 3.0, rel_tol=1e-9)

    def test_fourth_power_scaling_single_axle(self) -> None:
        """Doubling single-axle load (80 → 160 kN) must give LEF = 16."""
        group_base = _single(80.0)
        group_2x = _single(160.0)
        ratio = _lef_for_axle_group(group_2x) / _lef_for_axle_group(group_base)
        assert math.isclose(ratio, 16.0, rel_tol=1e-9)

    def test_fourth_power_scaling_tandem(self) -> None:
        """Doubling tandem load (160 → 320 kN) must give LEF ratio = 16."""
        group_base = _tandem(160.0)
        group_2x = _tandem(320.0)
        ratio = _lef_for_axle_group(group_2x) / _lef_for_axle_group(group_base)
        assert math.isclose(ratio, 16.0, rel_tol=1e-9)

    def test_known_single_axle_cat_777g_front(self) -> None:
        """CAT 777G front axle 155 kN → LEF ≈ 14.0918 (bench_01 workings)."""
        group = _single(155.0)
        expected = (155.0 / 80.0) ** 4
        assert math.isclose(_lef_for_axle_group(group), expected, rel_tol=1e-9)
        assert math.isclose(_lef_for_axle_group(group), 14.0918, rel_tol=1e-4)

    def test_known_tandem_cat_777g_rear(self) -> None:
        """CAT 777G rear tandem 760 kN → LEF ≈ 1018.1328 (bench_01 workings)."""
        group = _tandem(760.0)
        expected = (760.0 / 160.0) ** 4 * 2
        assert math.isclose(_lef_for_axle_group(group), expected, rel_tol=1e-9)
        assert math.isclose(_lef_for_axle_group(group), 1018.1328, rel_tol=1e-4)


# ---------------------------------------------------------------------------
# Tests: compute_cesa return type and metadata
# ---------------------------------------------------------------------------


class TestCesaResultMetadata:
    """Tests for CesaResult fields and method labelling."""

    def test_returns_cesa_result(self) -> None:
        vehicle = _make_vehicle("V", [_single(80.0)])
        result = compute_cesa(_make_traffic(vehicle))
        assert isinstance(result, CesaResult)

    def test_total_cesa_is_positive(self) -> None:
        vehicle = _make_vehicle("V", [_single(80.0)])
        result = compute_cesa(_make_traffic(vehicle))
        assert result.total_cesa > 0

    def test_method_contains_aashto(self) -> None:
        vehicle = _make_vehicle("V", [_single(80.0)])
        result = compute_cesa(_make_traffic(vehicle))
        assert "AASHTO" in result.method

    def test_method_contains_4th(self) -> None:
        vehicle = _make_vehicle("V", [_single(80.0)])
        result = compute_cesa(_make_traffic(vehicle))
        assert "4th" in result.method or "4th" in result.method.lower()

    def test_confidence_is_benchmark_tested(self) -> None:
        vehicle = _make_vehicle("V", [_single(80.0)])
        result = compute_cesa(_make_traffic(vehicle))
        assert result.confidence == "benchmark_tested"

    def test_result_is_immutable(self) -> None:
        """CesaResult is a frozen dataclass — mutation must raise."""
        vehicle = _make_vehicle("V", [_single(80.0)])
        result = compute_cesa(_make_traffic(vehicle))
        with pytest.raises((AttributeError, TypeError)):
            result.total_cesa = 0.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Tests: CESA values — standard axle identity
# ---------------------------------------------------------------------------


class TestCesaStandardAxle:
    """Verify that a standard 80 kN single axle gives the exact expected CESA."""

    def test_standard_single_axle_cesa(self) -> None:
        """Single vehicle, standard axle: CESA = trips × 1.0 × days × years."""
        vehicle = _make_vehicle("Standard", [_single(80.0)])
        traffic = _make_traffic(vehicle, trips=10, life_years=10, days_per_year=350)
        result = compute_cesa(traffic)
        expected = 10 * 1.0 * 350 * 10  # 35000
        assert math.isclose(result.total_cesa, expected, rel_tol=1e-9)

    def test_single_vehicle_single_trip_one_year_one_day(self) -> None:
        """Minimal case: 1 trip/day, 1 year, 1 day → CESA = LEF."""
        vehicle = _make_vehicle("Minimal", [_single(80.0)])
        traffic = _make_traffic(vehicle, trips=1, life_years=1, days_per_year=1)
        result = compute_cesa(traffic)
        assert math.isclose(result.total_cesa, 1.0, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# Tests: CESA scaling properties
# ---------------------------------------------------------------------------


class TestCesaScalingProperties:
    """Verify linear and 4th-power scaling behaviours."""

    def test_linear_in_trips_per_day(self) -> None:
        """Doubling trips_per_day must double CESA."""
        vehicle = _make_vehicle("V", [_single(100.0)])
        r1 = compute_cesa(_make_traffic(vehicle, trips=10))
        r2 = compute_cesa(_make_traffic(vehicle, trips=20))
        assert math.isclose(r2.total_cesa / r1.total_cesa, 2.0, rel_tol=1e-9)

    def test_linear_in_design_life(self) -> None:
        """Doubling design_life_years must double CESA."""
        vehicle = _make_vehicle("V", [_single(100.0)])
        r1 = compute_cesa(_make_traffic(vehicle, life_years=5))
        r2 = compute_cesa(_make_traffic(vehicle, life_years=10))
        assert math.isclose(r2.total_cesa / r1.total_cesa, 2.0, rel_tol=1e-9)

    def test_linear_in_working_days(self) -> None:
        """Doubling working_days_per_year must double CESA."""
        vehicle = _make_vehicle("V", [_single(100.0)])
        r1 = compute_cesa(_make_traffic(vehicle, days_per_year=175))
        r2 = compute_cesa(_make_traffic(vehicle, days_per_year=350))
        assert math.isclose(r2.total_cesa / r1.total_cesa, 2.0, rel_tol=1e-9)

    def test_fourth_power_single_axle_load(self) -> None:
        """Doubling single-axle load → CESA ratio = 16."""
        v_base = _make_vehicle("Base", [_single(80.0)])
        v_2x = _make_vehicle("2x", [_single(160.0)])
        r_base = compute_cesa(_make_traffic(v_base, trips=10))
        r_2x = compute_cesa(_make_traffic(v_2x, trips=10))
        assert math.isclose(r_2x.total_cesa / r_base.total_cesa, 16.0, rel_tol=1e-9)

    def test_fourth_power_tandem_load(self) -> None:
        """Doubling tandem group load → CESA ratio = 16."""
        v_base = _make_vehicle("Base", [_tandem(160.0)])
        v_2x = _make_vehicle("2x", [_tandem(320.0)])
        r_base = compute_cesa(_make_traffic(v_base, trips=10))
        r_2x = compute_cesa(_make_traffic(v_2x, trips=10))
        assert math.isclose(r_2x.total_cesa / r_base.total_cesa, 16.0, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# Tests: multi-vehicle fleet additive behaviour
# ---------------------------------------------------------------------------


class TestMultiVehicleFleet:
    """CESA for a fleet must equal the sum of individual vehicle CESAs."""

    def test_two_vehicle_fleet_additivity(self) -> None:
        v1 = _make_vehicle("V1", [_single(100.0)])
        v2 = _make_vehicle("V2", [_tandem(200.0)])
        traffic_combined = TrafficInput(
            fleet=[
                FleetUnit(vehicle=v1, trips_per_day=10),
                FleetUnit(vehicle=v2, trips_per_day=5),
            ],
            design_life_years=10,
            working_days_per_year=350,
        )
        r_combined = compute_cesa(traffic_combined)

        r1 = compute_cesa(_make_traffic(v1, trips=10))
        r2 = compute_cesa(_make_traffic(v2, trips=5))
        assert math.isclose(
            r_combined.total_cesa, r1.total_cesa + r2.total_cesa, rel_tol=1e-9
        )

    def test_fleet_ordering_does_not_matter(self) -> None:
        """CESA must be the same regardless of FleetUnit order."""
        v1 = _make_vehicle("V1", [_single(100.0)])
        v2 = _make_vehicle("V2", [_tandem(200.0)])
        t_ab = TrafficInput(
            fleet=[
                FleetUnit(vehicle=v1, trips_per_day=10),
                FleetUnit(vehicle=v2, trips_per_day=5),
            ],
            design_life_years=10,
            working_days_per_year=350,
        )
        t_ba = TrafficInput(
            fleet=[
                FleetUnit(vehicle=v2, trips_per_day=5),
                FleetUnit(vehicle=v1, trips_per_day=10),
            ],
            design_life_years=10,
            working_days_per_year=350,
        )
        assert math.isclose(
            compute_cesa(t_ab).total_cesa, compute_cesa(t_ba).total_cesa, rel_tol=1e-9
        )


# ---------------------------------------------------------------------------
# Tests: multi-axle vehicle
# ---------------------------------------------------------------------------


class TestMultiAxleVehicle:
    """Vehicles with multiple axle groups."""

    def test_two_axle_groups_summed(self) -> None:
        """CESA from a 2-group vehicle must equal the sum of the two group CESAs."""
        v_combined = _make_vehicle("Combined", [_single(100.0), _tandem(200.0)])
        v_single_only = _make_vehicle("Single", [_single(100.0)])
        v_tandem_only = _make_vehicle("Tandem", [_tandem(200.0)])

        r_combined = compute_cesa(_make_traffic(v_combined, trips=10))
        r_s = compute_cesa(_make_traffic(v_single_only, trips=10))
        r_t = compute_cesa(_make_traffic(v_tandem_only, trips=10))
        assert math.isclose(
            r_combined.total_cesa, r_s.total_cesa + r_t.total_cesa, rel_tol=1e-9
        )

    def test_three_axle_groups(self) -> None:
        """A vehicle with three axle groups must compute a positive CESA."""
        v = _make_vehicle("Triple", [_single(80.0), _tandem(160.0), _tridem(240.0)])
        result = compute_cesa(_make_traffic(v, trips=1, life_years=1, days_per_year=1))
        # LEF: 1.0 + 2.0 + 3.0 = 6.0; CESA = 1 × 6.0 × 1 × 1 = 6.0
        assert math.isclose(result.total_cesa, 6.0, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# Tests: edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge cases: single trip, very long design life, fractional days, etc."""

    def test_single_trip_per_day(self) -> None:
        vehicle = _make_vehicle("V", [_single(80.0)])
        result = compute_cesa(_make_traffic(vehicle, trips=1, life_years=1, days_per_year=365))
        assert math.isclose(result.total_cesa, 365.0, rel_tol=1e-9)

    def test_long_design_life(self) -> None:
        """50-year design life should give 5× the CESA of 10-year design life."""
        vehicle = _make_vehicle("V", [_single(100.0)])
        r10 = compute_cesa(_make_traffic(vehicle, life_years=10))
        r50 = compute_cesa(_make_traffic(vehicle, life_years=50))
        assert math.isclose(r50.total_cesa / r10.total_cesa, 5.0, rel_tol=1e-9)

    def test_fractional_trips_per_day(self) -> None:
        """trips_per_day may be non-integer (e.g. 0.5 trucks/day)."""
        vehicle = _make_vehicle("V", [_single(80.0)])
        r_half = compute_cesa(_make_traffic(vehicle, trips=0.5, life_years=10, days_per_year=350))
        r_one = compute_cesa(_make_traffic(vehicle, trips=1.0, life_years=10, days_per_year=350))
        assert math.isclose(r_half.total_cesa * 2, r_one.total_cesa, rel_tol=1e-9)

    def test_total_cesa_is_float(self) -> None:
        vehicle = _make_vehicle("V", [_single(80.0)])
        result = compute_cesa(_make_traffic(vehicle))
        assert isinstance(result.total_cesa, float)

    def test_very_light_load(self) -> None:
        """Extremely light axle load (10 kN) must still give a positive CESA."""
        vehicle = _make_vehicle("Light", [_single(10.0)])
        result = compute_cesa(_make_traffic(vehicle, trips=1, life_years=1, days_per_year=1))
        expected_lef = (10.0 / 80.0) ** 4
        assert math.isclose(result.total_cesa, expected_lef, rel_tol=1e-9)
