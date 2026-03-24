"""Benchmark 01 — CESA hand-calc for 3 fleet compositions.

Source: AASHTO (1993) Guide for Design of Pavement Structures, 4th edition.
Method: 4th power law LEF. Standard single axle = 80 kN.
        Standard tandem axle group = 160 kN.
Hand-calculated 2026-03-24.

CESA (Cumulative Equivalent Standard Axles) is the total pavement loading
expressed as an equivalent number of 80 kN standard single-axle passes over
the design life of the road.

4th Power Law:
  LEF (single axle)  = (axle_load_kN / 80.0) ** 4
  LEF (tandem group) = (group_load_kN / 160.0) ** 4 * 2

CESA per vehicle per direction:
  CESA = trips_per_day × total_LEF × working_days_per_year × design_life_years

Total CESA = sum over all vehicle types in the fleet.

Design parameters used throughout: design_life=10 years, working_days=350/year.

-------------------------------------------------------------------------------
HAND-CALCULATION WORKINGS
-------------------------------------------------------------------------------

FLEET A — Light

  CAT 777G (GVM 186 t, 50 trips/day):
    Front single axle load  = 155 kN
    Rear tandem group load  = 760 kN
    Front LEF  = (155 / 80)^4 = (1.9375)^4 = 14.0918
    Rear LEF   = (760 / 160)^4 × 2 = (4.75)^4 × 2 = 509.0664 × 2 = 1018.1328
    Total LEF  = 14.0918 + 1018.1328 = 1032.2246
    CESA       = 50 × 1032.2246 × 350 × 10 = 180,639,309.31

  Water Truck (GVM 40 t, 10 trips/day):
    Front single axle load  = 120 kN
    Rear tandem group load  = 270 kN
    Front LEF  = (120 / 80)^4 = (1.5)^4 = 5.0625
    Rear LEF   = (270 / 160)^4 × 2 = (1.6875)^4 × 2 = 8.1091 × 2 = 16.2183
    Total LEF  = 5.0625 + 16.2183 = 21.2808
    CESA       = 10 × 21.2808 × 350 × 10 = 744,827.73

  Fleet A total CESA = 180,639,309.31 + 744,827.73 = 181,384,137.04

-------------------------------------------------------------------------------

FLEET B — Medium

  CAT 785D (GVM 269 t, 40 trips/day):
    Front single axle load  = 225 kN
    Rear tandem group load  = 1040 kN
    Front LEF  = (225 / 80)^4 = (2.8125)^4 = 62.5706
    Rear LEF   = (1040 / 160)^4 × 2 = (6.5)^4 × 2 = 1785.0625 × 2 = 3570.1250
    Total LEF  = 62.5706 + 3570.1250 = 3632.6956
    CESA       = 40 × 3632.6956 × 350 × 10 = 508,577,380.07

  Motor Grader (GVM 25 t, 5 trips/day):
    Front single axle load  = 85 kN
    Rear tandem group load  = 160 kN
    Front LEF  = (85 / 80)^4 = (1.0625)^4 = 1.2744
    Rear LEF   = (160 / 160)^4 × 2 = (1.0)^4 × 2 = 1.0000 × 2 = 2.0000
    Total LEF  = 1.2744 + 2.0000 = 3.2744
    CESA       = 5 × 3.2744 × 350 × 10 = 57,302.51

  Fleet B total CESA = 508,577,380.07 + 57,302.51 = 508,634,682.58

-------------------------------------------------------------------------------

FLEET C — Heavy

  CAT 793F (GVM 623 t loaded, 30 trips/day):
    Front single axle load  = 550 kN
    Rear tandem group load  = 1900 kN
    Front LEF  = (550 / 80)^4 = (6.875)^4 = 2234.0393
    Rear LEF   = (1900 / 160)^4 × 2 = (11.875)^4 × 2 = 19885.4065 × 2 = 39770.8130
    Total LEF  = 2234.0393 + 39770.8130 = 42004.8523
    CESA       = 30 × 42004.8523 × 350 × 10 = 4,410,509,490.97

  Fuel Truck (GVM 30 t, 15 trips/day):
    Front single axle load  = 100 kN
    Rear tandem group load  = 200 kN
    Front LEF  = (100 / 80)^4 = (1.25)^4 = 2.4414
    Rear LEF   = (200 / 160)^4 × 2 = (1.25)^4 × 2 = 2.4414 × 2 = 4.8828
    Total LEF  = 2.4414 + 4.8828 = 7.3242
    CESA       = 15 × 7.3242 × 350 × 10 = 384,521.48

  Fleet C total CESA = 4,410,509,490.97 + 384,521.48 = 4,410,894,012.45

-------------------------------------------------------------------------------
"""

from __future__ import annotations

import json
import math
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Import the (not yet implemented) CESA engine.
# pytest.importorskip causes the entire module to be skipped — not failed —
# when haulpave.traffic.cesa does not exist. CI stays green until DAS-101
# implements the engine.
# ---------------------------------------------------------------------------
cesa_mod = pytest.importorskip(
    "haulpave.traffic.cesa",
    reason="CESA engine not yet implemented — tracked in DAS-101",
)
compute_cesa = cesa_mod.compute_cesa

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
_REF = json.loads(
    (pathlib.Path(__file__).parent / "reference_data" / "bench_01_expected.json").read_text(
        encoding="utf-8"
    )
)

TOLERANCE = _REF["metadata"]["tolerance_pct"] / 100.0  # 1 % → 0.01
DESIGN_LIFE = _REF["metadata"]["design_life_years"]
WORKING_DAYS = _REF["metadata"]["working_days_per_year"]

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
from haulpave.models.traffic import FleetUnit, TrafficInput  # noqa: E402
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec  # noqa: E402

# A generic TireSpec placeholder — actual contact pressure / area values are
# not used by the CESA engine (only gross_load_kn matters for 4th power law).
_PLACEHOLDER_TIRE = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=50000.0)


def _single(load_kn: float) -> AxleGroup:
    """Single axle group with one axle."""
    return AxleGroup(
        axle_count=1,
        tyres_per_axle=2,
        gross_load_kn=load_kn,
        tire_spec=_PLACEHOLDER_TIRE,
    )


def _tandem(load_kn: float) -> AxleGroup:
    """Tandem axle group (2 axles)."""
    return AxleGroup(
        axle_count=2,
        tyres_per_axle=4,
        gross_load_kn=load_kn,
        tire_spec=_PLACEHOLDER_TIRE,
    )


# ---------------------------------------------------------------------------
# Fleet A — Light
# ---------------------------------------------------------------------------
@pytest.fixture()
def fleet_a_input() -> TrafficInput:
    """Fleet A: CAT 777G + Water Truck."""
    cat_777g = MiningVehicle(
        name="CAT 777G",
        gross_vehicle_mass_t=186.0,
        axle_groups=[
            _single(155.0),  # front single axle: 155 kN
            _tandem(760.0),  # rear tandem group: 760 kN
        ],
        source="Caterpillar 777G Specifications, CAT Performance Handbook Ed. 47",
    )
    water_truck = MiningVehicle(
        name="Water Truck (40 t)",
        gross_vehicle_mass_t=40.0,
        axle_groups=[
            _single(120.0),  # front single axle: 120 kN
            _tandem(270.0),  # rear tandem group: 270 kN
        ],
        source="Generic mining water truck — conservative estimate based on GVM",
    )
    return TrafficInput(
        fleet=[
            FleetUnit(vehicle=cat_777g, trips_per_day=50),
            FleetUnit(vehicle=water_truck, trips_per_day=10),
        ],
        design_life_years=DESIGN_LIFE,
        working_days_per_year=WORKING_DAYS,
    )


# ---------------------------------------------------------------------------
# Fleet B — Medium
# ---------------------------------------------------------------------------
@pytest.fixture()
def fleet_b_input() -> TrafficInput:
    """Fleet B: CAT 785D + Motor Grader."""
    cat_785d = MiningVehicle(
        name="CAT 785D",
        gross_vehicle_mass_t=269.0,
        axle_groups=[
            _single(225.0),  # front single axle: 225 kN
            _tandem(1040.0),  # rear tandem group: 1040 kN
        ],
        source="Caterpillar 785D Specifications, CAT Performance Handbook Ed. 47",
    )
    motor_grader = MiningVehicle(
        name="Motor Grader (25 t)",
        gross_vehicle_mass_t=25.0,
        axle_groups=[
            _single(85.0),  # front single axle: 85 kN
            _tandem(160.0),  # rear tandem group: 160 kN (= standard tandem → LEF 2.0)
        ],
        source="Generic motor grader — conservative estimate based on GVM",
    )
    return TrafficInput(
        fleet=[
            FleetUnit(vehicle=cat_785d, trips_per_day=40),
            FleetUnit(vehicle=motor_grader, trips_per_day=5),
        ],
        design_life_years=DESIGN_LIFE,
        working_days_per_year=WORKING_DAYS,
    )


# ---------------------------------------------------------------------------
# Fleet C — Heavy
# ---------------------------------------------------------------------------
@pytest.fixture()
def fleet_c_input() -> TrafficInput:
    """Fleet C: CAT 793F + Fuel Truck."""
    cat_793f = MiningVehicle(
        name="CAT 793F",
        gross_vehicle_mass_t=623.0,
        axle_groups=[
            _single(550.0),  # front single axle: 550 kN
            _tandem(1900.0),  # rear tandem group: 1900 kN
        ],
        source="Caterpillar 793F Specifications, CAT Performance Handbook Ed. 47",
    )
    fuel_truck = MiningVehicle(
        name="Fuel Truck (30 t)",
        gross_vehicle_mass_t=30.0,
        axle_groups=[
            _single(100.0),  # front single axle: 100 kN
            _tandem(200.0),  # rear tandem group: 200 kN
        ],
        source="Generic mining fuel truck — conservative estimate based on GVM",
    )
    return TrafficInput(
        fleet=[
            FleetUnit(vehicle=cat_793f, trips_per_day=30),
            FleetUnit(vehicle=fuel_truck, trips_per_day=15),
        ],
        design_life_years=DESIGN_LIFE,
        working_days_per_year=WORKING_DAYS,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _assert_close(computed: float, expected: float, label: str) -> None:
    """Assert computed value is within TOLERANCE of expected hand-calc."""
    relative_error = abs(computed - expected) / expected
    assert relative_error <= TOLERANCE, (
        f"{label}: computed={computed:.2f}, expected={expected:.2f}, "
        f"relative error={relative_error:.4%} (tolerance={TOLERANCE:.1%})"
    )


class TestFleetALight:
    """Fleet A — Light (CAT 777G + Water Truck) CESA benchmark."""

    def test_total_cesa(self, fleet_a_input: TrafficInput) -> None:
        result = compute_cesa(fleet_a_input)
        expected = _REF["fleets"]["fleet_a_light"]["total_cesa"]
        _assert_close(result.total_cesa, expected, "Fleet A total_cesa")

    def test_total_cesa_order_of_magnitude(self, fleet_a_input: TrafficInput) -> None:
        """Fleet A should be in the ~1.8 × 10^8 range."""
        result = compute_cesa(fleet_a_input)
        assert 1e7 < result.total_cesa < 1e9, (
            f"Fleet A CESA {result.total_cesa:.2e} outside expected order of magnitude"
        )

    def test_method_tag(self, fleet_a_input: TrafficInput) -> None:
        result = compute_cesa(fleet_a_input)
        assert "AASHTO" in result.method or "4th" in result.method.lower(), (
            f"Expected AASHTO/4th-power method tag, got: {result.method!r}"
        )


class TestFleetBMedium:
    """Fleet B — Medium (CAT 785D + Motor Grader) CESA benchmark."""

    def test_total_cesa(self, fleet_b_input: TrafficInput) -> None:
        result = compute_cesa(fleet_b_input)
        expected = _REF["fleets"]["fleet_b_medium"]["total_cesa"]
        _assert_close(result.total_cesa, expected, "Fleet B total_cesa")

    def test_total_cesa_order_of_magnitude(self, fleet_b_input: TrafficInput) -> None:
        """Fleet B should be in the ~5 × 10^8 range."""
        result = compute_cesa(fleet_b_input)
        assert 1e7 < result.total_cesa < 1e10, (
            f"Fleet B CESA {result.total_cesa:.2e} outside expected order of magnitude"
        )

    def test_fleet_b_greater_than_fleet_a(
        self,
        fleet_a_input: TrafficInput,
        fleet_b_input: TrafficInput,
    ) -> None:
        """Heavier fleet (B) must produce higher CESA than lighter fleet (A)."""
        result_a = compute_cesa(fleet_a_input)
        result_b = compute_cesa(fleet_b_input)
        assert result_b.total_cesa > result_a.total_cesa, (
            "Fleet B (medium) CESA should exceed Fleet A (light)"
        )


class TestFleetCHeavy:
    """Fleet C — Heavy (CAT 793F + Fuel Truck) CESA benchmark."""

    def test_total_cesa(self, fleet_c_input: TrafficInput) -> None:
        result = compute_cesa(fleet_c_input)
        expected = _REF["fleets"]["fleet_c_heavy"]["total_cesa"]
        _assert_close(result.total_cesa, expected, "Fleet C total_cesa")

    def test_total_cesa_order_of_magnitude(self, fleet_c_input: TrafficInput) -> None:
        """Fleet C should be in the ~4.4 × 10^9 range."""
        result = compute_cesa(fleet_c_input)
        assert 1e8 < result.total_cesa < 1e11, (
            f"Fleet C CESA {result.total_cesa:.2e} outside expected order of magnitude"
        )

    def test_fleet_c_greater_than_fleet_b(
        self,
        fleet_b_input: TrafficInput,
        fleet_c_input: TrafficInput,
    ) -> None:
        """Heaviest fleet (C) must produce higher CESA than medium fleet (B)."""
        result_b = compute_cesa(fleet_b_input)
        result_c = compute_cesa(fleet_c_input)
        assert result_c.total_cesa > result_b.total_cesa, (
            "Fleet C (heavy) CESA should exceed Fleet B (medium)"
        )


class TestCesaScaling:
    """Cross-fleet checks that verify 4th-power scaling behaviour."""

    def test_cesa_proportional_to_trips(self) -> None:
        """Doubling trips_per_day must double CESA (linear relationship)."""
        vehicle = MiningVehicle(
            name="Test Vehicle",
            gross_vehicle_mass_t=50.0,
            axle_groups=[_single(100.0)],
            source="Synthetic test vehicle for scaling check",
        )
        input_1x = TrafficInput(
            fleet=[FleetUnit(vehicle=vehicle, trips_per_day=10)],
            design_life_years=DESIGN_LIFE,
            working_days_per_year=WORKING_DAYS,
        )
        input_2x = TrafficInput(
            fleet=[FleetUnit(vehicle=vehicle, trips_per_day=20)],
            design_life_years=DESIGN_LIFE,
            working_days_per_year=WORKING_DAYS,
        )
        result_1x = compute_cesa(input_1x)
        result_2x = compute_cesa(input_2x)
        ratio = result_2x.total_cesa / result_1x.total_cesa
        assert math.isclose(ratio, 2.0, rel_tol=1e-6), (
            f"Expected CESA ratio 2.0 when trips doubled, got {ratio:.6f}"
        )

    def test_fourth_power_law_single_axle(self) -> None:
        """Verify 4th-power scaling: doubling axle load → 16× LEF contribution."""
        vehicle_base = MiningVehicle(
            name="Base Vehicle",
            gross_vehicle_mass_t=20.0,
            axle_groups=[_single(80.0)],  # exactly 1 standard axle → LEF = 1.0
            source="Synthetic test vehicle for 4th power law check",
        )
        vehicle_2x = MiningVehicle(
            name="Double-Load Vehicle",
            gross_vehicle_mass_t=40.0,
            axle_groups=[_single(160.0)],  # 2× standard → LEF = 16.0
            source="Synthetic test vehicle for 4th power law check",
        )
        input_base = TrafficInput(
            fleet=[FleetUnit(vehicle=vehicle_base, trips_per_day=10)],
            design_life_years=DESIGN_LIFE,
            working_days_per_year=WORKING_DAYS,
        )
        input_2x = TrafficInput(
            fleet=[FleetUnit(vehicle=vehicle_2x, trips_per_day=10)],
            design_life_years=DESIGN_LIFE,
            working_days_per_year=WORKING_DAYS,
        )
        result_base = compute_cesa(input_base)
        result_2x = compute_cesa(input_2x)
        ratio = result_2x.total_cesa / result_base.total_cesa
        assert math.isclose(ratio, 16.0, rel_tol=1e-6), (
            f"Expected CESA ratio 16.0 for doubled single-axle load (4th power law), "
            f"got {ratio:.6f}"
        )
