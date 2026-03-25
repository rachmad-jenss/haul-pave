"""Benchmark 02 — USACE design coverages hand-calc (3 fleet compositions).

Source: USACE TM 5-822-12, Flexible Pavement Design for Airfields, para 3-2.
Method: Design vehicle = heaviest single wheel load in fleet.
        Pass-to-coverage weighting by 4th power of wheel load ratio.
Hand-calculated 2026-03-24.

USACE Design Coverages
======================
A "coverage" is one complete pass of the design wheel over every point in the
trafficked lane.  Because tyres do not perfectly overlap on successive passes,
one vehicle pass equates to a fraction of a coverage.  For haul-road design the
USACE approach converts all wheel loads into an equivalent number of design-wheel
passes using the 4th-power law:

  equiv_passes_per_vehicle_pass = Σ_wheels [ (wheel_load / design_wheel_load)^4 ]

where the sum is over every wheel position in the vehicle.

Design wheel load = heaviest single-wheel load in the fleet.

Single-wheel load derivation
-----------------------------
For each axle group:
  - front axle (single, 2 tyres): wheel_load = axle_load / 2
  - rear tandem (axle_count=2, tyres_per_axle=4, treated as dual tyres):
        total tyre count = axle_count × 2 × tyres_per_axle = 2 × 2 × 4 = 16
        wheel_load = group_load / (axle_count × 2 × tyres_per_axle)
        e.g. Fleet A rear: 760 / (2 × 2 × 4) = 760 / 16 = 47.5 kN

Wheel-position counting for the coverage formula
--------------------------------------------------
For coverage contribution (not load), each axle group contributes:
  - front axle:  1 wheel position  (one tyre track on the design line)
  - rear tandem: axle_count × tyres_per_axle = 2 × 4 = 8 wheel positions
    (dual-tyre stations share a contact patch and are counted as one position)

Daily equivalent design-wheel passes per vehicle type
------------------------------------------------------
  equiv_passes/day = trips_per_day × 2 (both directions)
                   × Σ_groups [ wheel_positions × (wheel_load / design_wheel_load)^4 ]

Total design coverages over design life
----------------------------------------
  total_coverages = Σ_vehicle_types(equiv_passes/day) × working_days × design_life

Design parameters: design_life = 10 years, working_days = 350 days/year.

-------------------------------------------------------------------------------
HAND-CALCULATION WORKINGS
-------------------------------------------------------------------------------

FLEET A — Light  (design wheel load = 77.5 kN, CAT 777G front)

  CAT 777G (GVM 186 t, 50 trips/day):
    Front axle load  = 155 kN  → wheel_load = 155 / 2 = 77.5 kN (2 tyres, 1 position)
    Rear tandem load = 760 kN  → wheel_load = 760 / 16 = 47.5 kN (8 positions)

    Front contribution/day:
      (77.5 / 77.5)^4 × 50 × 2 × 1 = 1.0000 × 100 = 100.0000

    Rear contribution/day:
      ratio = 47.5 / 77.5 = 0.612903...
      ratio^4 = 0.141113
      (47.5 / 77.5)^4 × 50 × 2 × 8 = 0.141113 × 800 = 112.8906

    CAT 777G subtotal = 100.0000 + 112.8906 = 212.8906 equiv passes/day

  Water Truck (GVM 40 t, 10 trips/day):
    Front axle load  = 120 kN  → wheel_load = 120 / 2 = 60.0 kN (2 tyres, 1 position)
    Rear tandem load = 270 kN  → wheel_load = 270 / 16 = 16.875 kN (8 positions)

    Front contribution/day:
      ratio = 60.0 / 77.5 = 0.774194...
      ratio^4 = 0.359251
      (60.0 / 77.5)^4 × 10 × 2 × 1 = 0.359251 × 20 = 7.1850

    Rear contribution/day:
      ratio = 16.875 / 77.5 = 0.217742...
      ratio^4 = 0.002248
      (16.875 / 77.5)^4 × 10 × 2 × 8 = 0.002248 × 160 = 0.3597

    Water Truck subtotal = 7.1850 + 0.3597 = 7.5447 equiv passes/day

  Fleet A total equiv passes/day = 212.8906 + 7.5447 = 220.4353
  Fleet A total coverages = 220.4353 × 350 × 10 = 771,523.33

-------------------------------------------------------------------------------

FLEET B — Medium  (design wheel load = 112.5 kN, CAT 785D front)

  CAT 785D (GVM 269 t, 40 trips/day):
    Front axle load   = 225 kN  → wheel_load = 225 / 2 = 112.5 kN (1 position)
    Rear tandem load  = 1040 kN → wheel_load = 1040 / 16 = 65.0 kN (8 positions)

    Front contribution/day:
      (112.5 / 112.5)^4 × 40 × 2 × 1 = 1.0000 × 80 = 80.0000

    Rear contribution/day:
      ratio = 65.0 / 112.5 = 0.577778...
      ratio^4 = 0.111441
      (65.0 / 112.5)^4 × 40 × 2 × 8 = 0.111441 × 640 = 71.3220

    CAT 785D subtotal = 80.0000 + 71.3220 = 151.3220 equiv passes/day

  Motor Grader (GVM 25 t, 5 trips/day):
    Front axle load  = 85 kN   → wheel_load = 85 / 2 = 42.5 kN (1 position)
    Rear tandem load = 160 kN  → wheel_load = 160 / 16 = 10.0 kN (8 positions)

    Front contribution/day:
      ratio = 42.5 / 112.5 = 0.377778...
      ratio^4 = 0.020368
      (42.5 / 112.5)^4 × 5 × 2 × 1 = 0.020368 × 10 = 0.2037

    Rear contribution/day:
      ratio = 10.0 / 112.5 = 0.088889...
      ratio^4 = 0.000062
      (10.0 / 112.5)^4 × 5 × 2 × 8 = 0.000062 × 80 = 0.0050

    Motor Grader subtotal = 0.2037 + 0.0050 = 0.2087 equiv passes/day

  Fleet B total equiv passes/day = 151.3220 + 0.2087 = 151.5307
  Fleet B total coverages = 151.5307 × 350 × 10 = 530,357.24

-------------------------------------------------------------------------------

FLEET C — Heavy  (design wheel load = 275.0 kN, CAT 793F front)

  CAT 793F (GVM 623 t, 30 trips/day):
    Front axle load  = 550 kN  → wheel_load = 550 / 2 = 275.0 kN (1 position)
    Rear tandem load = 1900 kN → wheel_load = 1900 / 16 = 118.75 kN (8 positions)

    Front contribution/day:
      (275.0 / 275.0)^4 × 30 × 2 × 1 = 1.0000 × 60 = 60.0000

    Rear contribution/day:
      ratio = 118.75 / 275.0 = 0.431818...
      ratio^4 = 0.034770
      (118.75 / 275.0)^4 × 30 × 2 × 8 = 0.034770 × 480 = 16.6896

    CAT 793F subtotal = 60.0000 + 16.6896 = 76.6896 equiv passes/day

  Fuel Truck (GVM 30 t, 15 trips/day):
    Front axle load  = 100 kN  → wheel_load = 100 / 2 = 50.0 kN (1 position)
    Rear tandem load = 200 kN  → wheel_load = 200 / 16 = 12.5 kN (8 positions)

    Front contribution/day:
      ratio = 50.0 / 275.0 = 0.181818...
      ratio^4 = 0.001093
      (50.0 / 275.0)^4 × 15 × 2 × 1 = 0.001093 × 30 = 0.0328

    Rear contribution/day:
      ratio = 12.5 / 275.0 = 0.045455...
      ratio^4 = 0.000004
      (12.5 / 275.0)^4 × 15 × 2 × 8 = 0.000004 × 240 = 0.0010

    Fuel Truck subtotal = 0.0328 + 0.0010 = 0.0338 equiv passes/day

  Fleet C total equiv passes/day = 76.6896 + 0.0338 = 76.7234
  Fleet C total coverages = 76.7234 × 350 × 10 = 268,531.80

-------------------------------------------------------------------------------
"""

from __future__ import annotations

import json
import math
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Import the (not yet implemented) coverages engine.
# pytest.importorskip causes the entire module to be skipped — not failed —
# when haulpave.traffic.coverages does not exist. CI stays green until DAS-102
# implements the engine.
# ---------------------------------------------------------------------------
coverages_mod = pytest.importorskip(
    "haulpave.traffic.coverages",
    reason="Coverages engine not yet implemented — tracked in DAS-102",
)
compute_coverages = coverages_mod.compute_coverages

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
_REF = json.loads(
    (pathlib.Path(__file__).parent / "reference_data" / "bench_02_expected.json").read_text(
        encoding="utf-8"
    )
)

TOLERANCE = _REF["metadata"]["tolerance_pct"] / 100.0  # 2 % → 0.02
DESIGN_LIFE = _REF["metadata"]["design_life_years"]
WORKING_DAYS = _REF["metadata"]["working_days_per_year"]

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
from haulpave.models.traffic import FleetUnit, TrafficInput  # noqa: E402
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec  # noqa: E402

# A generic TireSpec placeholder — the coverages engine uses gross_load_kn and
# axle/tyre counts; contact pressure / area are not needed for the USACE method.
_PLACEHOLDER_TIRE = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=50000.0)


def _single(load_kn: float) -> AxleGroup:
    """Single axle group: 1 axle, 2 tyres."""
    return AxleGroup(
        axle_count=1,
        tyres_per_axle=2,
        gross_load_kn=load_kn,
        tire_spec=_PLACEHOLDER_TIRE,
    )


def _tandem(load_kn: float) -> AxleGroup:
    """Tandem axle group: 2 axles, 4 tyres per axle (dual-tyre stations)."""
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
    """Fleet A: CAT 777G + Water Truck.

    Design wheel load = 77.5 kN (CAT 777G front axle ÷ 2 tyres).
    """
    cat_777g = MiningVehicle(
        name="CAT 777G",
        gross_vehicle_mass_t=186.0,
        axle_groups=[
            _single(155.0),  # front single axle: 155 kN → 77.5 kN/wheel
            _tandem(760.0),  # rear tandem group: 760 kN → 47.5 kN/wheel (16 tyres)
        ],
        source="Caterpillar 777G Specifications, CAT Performance Handbook Ed. 47",
    )
    water_truck = MiningVehicle(
        name="Water Truck (40 t)",
        gross_vehicle_mass_t=40.0,
        axle_groups=[
            _single(120.0),  # front single axle: 120 kN → 60.0 kN/wheel
            _tandem(270.0),  # rear tandem group: 270 kN → 16.875 kN/wheel (16 tyres)
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
    """Fleet B: CAT 785D + Motor Grader.

    Design wheel load = 112.5 kN (CAT 785D front axle ÷ 2 tyres).
    """
    cat_785d = MiningVehicle(
        name="CAT 785D",
        gross_vehicle_mass_t=269.0,
        axle_groups=[
            _single(225.0),  # front single axle: 225 kN → 112.5 kN/wheel
            _tandem(1040.0),  # rear tandem group: 1040 kN → 65.0 kN/wheel (16 tyres)
        ],
        source="Caterpillar 785D Specifications, CAT Performance Handbook Ed. 47",
    )
    motor_grader = MiningVehicle(
        name="Motor Grader (25 t)",
        gross_vehicle_mass_t=25.0,
        axle_groups=[
            _single(85.0),  # front single axle: 85 kN → 42.5 kN/wheel
            _tandem(160.0),  # rear tandem group: 160 kN → 10.0 kN/wheel (16 tyres)
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
    """Fleet C: CAT 793F + Fuel Truck.

    Design wheel load = 275.0 kN (CAT 793F front axle ÷ 2 tyres).
    """
    cat_793f = MiningVehicle(
        name="CAT 793F",
        gross_vehicle_mass_t=623.0,
        axle_groups=[
            _single(550.0),  # front single axle: 550 kN → 275.0 kN/wheel
            _tandem(1900.0),  # rear tandem group: 1900 kN → 118.75 kN/wheel (16 tyres)
        ],
        source="Caterpillar 793F Specifications, CAT Performance Handbook Ed. 47",
    )
    fuel_truck = MiningVehicle(
        name="Fuel Truck (30 t)",
        gross_vehicle_mass_t=30.0,
        axle_groups=[
            _single(100.0),  # front single axle: 100 kN → 50.0 kN/wheel
            _tandem(200.0),  # rear tandem group: 200 kN → 12.5 kN/wheel (16 tyres)
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
# Shared assertion helper
# ---------------------------------------------------------------------------
def _assert_close(computed: float, expected: float, label: str) -> None:
    """Assert computed value is within TOLERANCE of expected hand-calc."""
    relative_error = abs(computed - expected) / expected
    assert relative_error <= TOLERANCE, (
        f"{label}: computed={computed:.2f}, expected={expected:.2f}, "
        f"relative error={relative_error:.4%} (tolerance={TOLERANCE:.1%})"
    )


# ---------------------------------------------------------------------------
# Tests — Fleet A
# ---------------------------------------------------------------------------
class TestFleetALight:
    """Fleet A — Light (CAT 777G + Water Truck) coverages benchmark."""

    def test_total_coverages(self, fleet_a_input: TrafficInput) -> None:
        result = compute_coverages(fleet_a_input)
        expected = _REF["fleets"]["fleet_a_light"]["total_coverages"]
        _assert_close(result.total_coverages, expected, "Fleet A total_coverages")

    def test_total_coverages_order_of_magnitude(self, fleet_a_input: TrafficInput) -> None:
        """Fleet A coverages should be in the ~7.7 × 10^5 range."""
        result = compute_coverages(fleet_a_input)
        assert 1e5 < result.total_coverages < 1e7, (
            f"Fleet A coverages {result.total_coverages:.2e} outside expected order of magnitude"
        )

    def test_method_tag(self, fleet_a_input: TrafficInput) -> None:
        result = compute_coverages(fleet_a_input)
        assert "USACE" in result.method or "coverage" in result.method.lower(), (
            f"Expected USACE/coverage method tag, got: {result.method!r}"
        )

    def test_design_wheel_load(self, fleet_a_input: TrafficInput) -> None:
        """Fleet A design wheel load must be 77.5 kN (CAT 777G front axle ÷ 2)."""
        result = compute_coverages(fleet_a_input)
        expected_dwl = _REF["fleets"]["fleet_a_light"]["design_wheel_load_kN"]
        assert math.isclose(result.design_wheel_load_kn, expected_dwl, rel_tol=1e-4), (
            f"Fleet A design_wheel_load_kn: got {result.design_wheel_load_kn}, "
            f"expected {expected_dwl}"
        )


# ---------------------------------------------------------------------------
# Tests — Fleet B
# ---------------------------------------------------------------------------
class TestFleetBMedium:
    """Fleet B — Medium (CAT 785D + Motor Grader) coverages benchmark."""

    def test_total_coverages(self, fleet_b_input: TrafficInput) -> None:
        result = compute_coverages(fleet_b_input)
        expected = _REF["fleets"]["fleet_b_medium"]["total_coverages"]
        _assert_close(result.total_coverages, expected, "Fleet B total_coverages")

    def test_total_coverages_order_of_magnitude(self, fleet_b_input: TrafficInput) -> None:
        """Fleet B coverages should be in the ~5.3 × 10^5 range."""
        result = compute_coverages(fleet_b_input)
        assert 1e4 < result.total_coverages < 1e7, (
            f"Fleet B coverages {result.total_coverages:.2e} outside expected order of magnitude"
        )

    def test_design_wheel_load(self, fleet_b_input: TrafficInput) -> None:
        """Fleet B design wheel load must be 112.5 kN (CAT 785D front axle ÷ 2)."""
        result = compute_coverages(fleet_b_input)
        expected_dwl = _REF["fleets"]["fleet_b_medium"]["design_wheel_load_kN"]
        assert math.isclose(result.design_wheel_load_kn, expected_dwl, rel_tol=1e-4), (
            f"Fleet B design_wheel_load_kn: got {result.design_wheel_load_kn}, "
            f"expected {expected_dwl}"
        )

    def test_fleet_b_less_than_fleet_a(
        self,
        fleet_a_input: TrafficInput,
        fleet_b_input: TrafficInput,
    ) -> None:
        """Fleet B has fewer daily passes than Fleet A → lower coverages expected."""
        result_a = compute_coverages(fleet_a_input)
        result_b = compute_coverages(fleet_b_input)
        assert result_b.total_coverages < result_a.total_coverages, (
            "Fleet B coverages should be less than Fleet A (fewer trips, heavier loads "
            "are relatively damped by the 4th-power weighting against a heavier design wheel)"
        )


# ---------------------------------------------------------------------------
# Tests — Fleet C
# ---------------------------------------------------------------------------
class TestFleetCHeavy:
    """Fleet C — Heavy (CAT 793F + Fuel Truck) coverages benchmark."""

    def test_total_coverages(self, fleet_c_input: TrafficInput) -> None:
        result = compute_coverages(fleet_c_input)
        expected = _REF["fleets"]["fleet_c_heavy"]["total_coverages"]
        _assert_close(result.total_coverages, expected, "Fleet C total_coverages")

    def test_total_coverages_order_of_magnitude(self, fleet_c_input: TrafficInput) -> None:
        """Fleet C coverages should be in the ~2.7 × 10^5 range."""
        result = compute_coverages(fleet_c_input)
        assert 1e4 < result.total_coverages < 1e7, (
            f"Fleet C coverages {result.total_coverages:.2e} outside expected order of magnitude"
        )

    def test_design_wheel_load(self, fleet_c_input: TrafficInput) -> None:
        """Fleet C design wheel load must be 275.0 kN (CAT 793F front axle ÷ 2)."""
        result = compute_coverages(fleet_c_input)
        expected_dwl = _REF["fleets"]["fleet_c_heavy"]["design_wheel_load_kN"]
        assert math.isclose(result.design_wheel_load_kn, expected_dwl, rel_tol=1e-4), (
            f"Fleet C design_wheel_load_kn: got {result.design_wheel_load_kn}, "
            f"expected {expected_dwl}"
        )

    def test_fleet_c_less_than_fleet_a(
        self,
        fleet_a_input: TrafficInput,
        fleet_c_input: TrafficInput,
    ) -> None:
        """Fleet C has fewer daily passes than Fleet A → lower coverages expected."""
        result_a = compute_coverages(fleet_a_input)
        result_c = compute_coverages(fleet_c_input)
        assert result_c.total_coverages < result_a.total_coverages, (
            "Fleet C coverages should be less than Fleet A (fewer trips per day)"
        )


# ---------------------------------------------------------------------------
# Tests — Scaling behaviour
# ---------------------------------------------------------------------------
class TestCoveragesScaling:
    """Cross-fleet checks verifying 4th-power scaling and linearity."""

    def test_coverages_proportional_to_trips(self) -> None:
        """Doubling trips_per_day must double total coverages (linear relationship)."""
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
        result_1x = compute_coverages(input_1x)
        result_2x = compute_coverages(input_2x)
        ratio = result_2x.total_coverages / result_1x.total_coverages
        assert math.isclose(ratio, 2.0, rel_tol=1e-6), (
            f"Expected coverages ratio 2.0 when trips doubled, got {ratio:.6f}"
        )

    def test_fourth_power_weighting_single_axle(self) -> None:
        """4th-power weighting: halving wheel load reduces coverage contribution by 1/16."""
        # Design vehicle: single axle 200 kN → wheel_load = 100 kN
        design_vehicle = MiningVehicle(
            name="Design Vehicle",
            gross_vehicle_mass_t=30.0,
            axle_groups=[_single(200.0)],
            source="Synthetic test vehicle for 4th power coverage check",
        )
        # Light vehicle: wheel_load = 50 kN = half of design wheel (100 kN)
        # Expected coverage contribution ratio = (50/100)^4 = 1/16 = 0.0625
        light_vehicle = MiningVehicle(
            name="Half-Load Vehicle",
            gross_vehicle_mass_t=15.0,
            axle_groups=[_single(100.0)],
            source="Synthetic test vehicle for 4th power coverage check",
        )
        input_design = TrafficInput(
            fleet=[FleetUnit(vehicle=design_vehicle, trips_per_day=10)],
            design_life_years=DESIGN_LIFE,
            working_days_per_year=WORKING_DAYS,
        )
        # Mixed fleet: design vehicle + light vehicle at same trips
        input_mixed = TrafficInput(
            fleet=[
                FleetUnit(vehicle=design_vehicle, trips_per_day=10),
                FleetUnit(vehicle=light_vehicle, trips_per_day=10),
            ],
            design_life_years=DESIGN_LIFE,
            working_days_per_year=WORKING_DAYS,
        )
        result_design = compute_coverages(input_design)
        result_mixed = compute_coverages(input_mixed)
        # Mixed should be design + (1/16 × design) = 1.0625 × design
        expected_ratio = 1.0 + (0.5**4)  # 1 + 1/16 = 1.0625
        actual_ratio = result_mixed.total_coverages / result_design.total_coverages
        assert math.isclose(actual_ratio, expected_ratio, rel_tol=1e-5), (
            f"Expected coverage ratio {expected_ratio:.6f} (4th-power weighting), "
            f"got {actual_ratio:.6f}"
        )
