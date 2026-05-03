"""Benchmark 06 — Economics compare_scenarios hand-calc.

Method: Rolling-resistance (RR) linear cost model.

Rolling-resistance coefficients:
    asphalt  : 1.5 %  (RR = 0.015)
    concrete : 1.2 %  (RR = 0.012)
    gravel   : 4.0 %  (RR = 0.040)

Calibrated linear model (per km per vehicle):
    fuel_l_per_km    = 2.042 + 29.2 × RR
    tyre_usd_per_km  = 0.128 + 92.8 × RR
    maint_usd_per_km = 0.144 + 30.4 × RR

Annual cost = cost_per_km × haul_distance_km × trips_per_day × working_days_per_year

Test scenario: 10 km haul, 40 trips/day, 250 working days/year, fuel $0.80/L
    km_per_year = 10 × 40 × 250 = 100,000 km/yr

ASPHALT (RR=0.015):
    fuel_l_per_km    = 2.042 + 29.2 × 0.015 = 2.480 L/km
    tyre_usd_per_km  = 0.128 + 92.8 × 0.015 = 1.520 USD/km
    maint_usd_per_km = 0.144 + 30.4 × 0.015 = 0.600 USD/km
    fuel_cost_yr  = 2.480 × 0.80 × 100,000 = 198,400 USD/yr
    tyre_cost_yr  = 1.520 × 100,000         = 152,000 USD/yr
    maint_cost_yr = 0.600 × 100,000         =  60,000 USD/yr

GRAVEL (RR=0.040):
    fuel_l_per_km    = 2.042 + 29.2 × 0.040 = 3.210 L/km
    tyre_usd_per_km  = 0.128 + 92.8 × 0.040 = 3.840 USD/km
    maint_usd_per_km = 0.144 + 30.4 × 0.040 = 1.360 USD/km
    fuel_cost_yr  = 3.210 × 0.80 × 100,000 = 256,800 USD/yr
    tyre_cost_yr  = 3.840 × 100,000         = 384,000 USD/yr
    maint_cost_yr = 1.360 × 100,000         = 136,000 USD/yr

CONCRETE (RR=0.012):
    fuel_l_per_km    = 2.042 + 29.2 × 0.012 = 2.3924 L/km
    tyre_usd_per_km  = 0.128 + 92.8 × 0.012 = 1.2416 USD/km
    maint_usd_per_km = 0.144 + 30.4 × 0.012 = 0.5088 USD/km
    fuel_cost_yr  = 2.3924 × 0.80 × 100,000 = 191,392 USD/yr
    tyre_cost_yr  = 1.2416 × 100,000         = 124,160 USD/yr
    maint_cost_yr = 0.5088 × 100,000         =  50,880 USD/yr

Ordering invariant (confirmed by RR physics):
    gravel > asphalt > concrete in all cost categories.
"""

from __future__ import annotations

import json
import pathlib

import pytest

compare_mod = pytest.importorskip(
    "haulpave.economics.compare",
    reason="economics.compare not yet implemented — tracked in DAS-268",
)
compare_scenarios = compare_mod.compare_scenarios
RoadScenario = compare_mod.RoadScenario

_REF = json.loads(
    (pathlib.Path(__file__).parent / "reference_data" / "bench_06_expected.json").read_text(
        encoding="utf-8"
    )
)

TOLERANCE = _REF["metadata"]["tolerance_pct"] / 100.0  # 0.1 % → 0.001
HAUL_KM = _REF["metadata"]["test_scenario"]["haul_distance_km"]
TRIPS_PER_DAY = _REF["metadata"]["test_scenario"]["trips_per_day"]


def _assert_close(computed: float, expected: float, label: str) -> None:
    relative_error = abs(computed - expected) / expected
    assert relative_error <= TOLERANCE, (
        f"{label}: computed={computed:.2f}, expected={expected:.2f}, "
        f"relative error={relative_error:.6%} (tolerance={TOLERANCE:.2%})"
    )


@pytest.fixture()
def three_surface_scenarios() -> list[RoadScenario]:
    return [
        RoadScenario(
            name="Asphalt",
            surface="asphalt",
            thickness_mm=100,
            haul_distance_km=HAUL_KM,
            trips_per_day=TRIPS_PER_DAY,
        ),
        RoadScenario(
            name="Gravel",
            surface="gravel",
            thickness_mm=600,
            haul_distance_km=HAUL_KM,
            trips_per_day=TRIPS_PER_DAY,
        ),
        RoadScenario(
            name="Concrete",
            surface="concrete",
            thickness_mm=200,
            haul_distance_km=HAUL_KM,
            trips_per_day=TRIPS_PER_DAY,
        ),
    ]


class TestAsphaltBenchmark:
    """Asphalt scenario (RR=1.5%) absolute cost values."""

    def test_fuel_cost(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        asphalt = next(s for s in result.scenarios if s.name == "Asphalt")
        expected = _REF["scenarios"]["asphalt"]["fuel_cost_usd_per_year"]
        _assert_close(asphalt.fuel_cost_usd_per_year, expected, "Asphalt fuel_cost_usd_per_year")

    def test_tyre_cost(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        asphalt = next(s for s in result.scenarios if s.name == "Asphalt")
        expected = _REF["scenarios"]["asphalt"]["tire_cost_usd_per_year"]
        _assert_close(asphalt.tire_cost_usd_per_year, expected, "Asphalt tire_cost_usd_per_year")

    def test_maintenance_cost(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        asphalt = next(s for s in result.scenarios if s.name == "Asphalt")
        expected = _REF["scenarios"]["asphalt"]["maintenance_cost_usd_per_year"]
        _assert_close(
            asphalt.maintenance_cost_usd_per_year,
            expected,
            "Asphalt maintenance_cost_usd_per_year",
        )


class TestGravelBenchmark:
    """Gravel scenario (RR=4.0%) absolute cost values."""

    def test_fuel_cost(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        gravel = next(s for s in result.scenarios if s.name == "Gravel")
        expected = _REF["scenarios"]["gravel"]["fuel_cost_usd_per_year"]
        _assert_close(gravel.fuel_cost_usd_per_year, expected, "Gravel fuel_cost_usd_per_year")

    def test_tyre_cost(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        gravel = next(s for s in result.scenarios if s.name == "Gravel")
        expected = _REF["scenarios"]["gravel"]["tire_cost_usd_per_year"]
        _assert_close(gravel.tire_cost_usd_per_year, expected, "Gravel tire_cost_usd_per_year")

    def test_maintenance_cost(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        gravel = next(s for s in result.scenarios if s.name == "Gravel")
        expected = _REF["scenarios"]["gravel"]["maintenance_cost_usd_per_year"]
        _assert_close(
            gravel.maintenance_cost_usd_per_year,
            expected,
            "Gravel maintenance_cost_usd_per_year",
        )


class TestConcreteBenchmark:
    """Concrete scenario (RR=1.2%) absolute cost values."""

    def test_fuel_cost(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        concrete = next(s for s in result.scenarios if s.name == "Concrete")
        expected = _REF["scenarios"]["concrete"]["fuel_cost_usd_per_year"]
        _assert_close(concrete.fuel_cost_usd_per_year, expected, "Concrete fuel_cost_usd_per_year")

    def test_tyre_cost(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        concrete = next(s for s in result.scenarios if s.name == "Concrete")
        expected = _REF["scenarios"]["concrete"]["tire_cost_usd_per_year"]
        _assert_close(concrete.tire_cost_usd_per_year, expected, "Concrete tire_cost_usd_per_year")

    def test_maintenance_cost(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        concrete = next(s for s in result.scenarios if s.name == "Concrete")
        expected = _REF["scenarios"]["concrete"]["maintenance_cost_usd_per_year"]
        _assert_close(
            concrete.maintenance_cost_usd_per_year,
            expected,
            "Concrete maintenance_cost_usd_per_year",
        )


class TestOrderingInvariants:
    """Physics ordering: concrete < asphalt < gravel in all cost categories."""

    def test_gravel_fuel_exceeds_asphalt(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        by_name = {s.name: s for s in result.scenarios}
        assert by_name["Gravel"].fuel_cost_usd_per_year > by_name["Asphalt"].fuel_cost_usd_per_year

    def test_asphalt_fuel_exceeds_concrete(
        self, three_surface_scenarios: list[RoadScenario]
    ) -> None:
        result = compare_scenarios(three_surface_scenarios)
        by_name = {s.name: s for s in result.scenarios}
        assert (
            by_name["Asphalt"].fuel_cost_usd_per_year > by_name["Concrete"].fuel_cost_usd_per_year
        )

    def test_gravel_tyre_exceeds_asphalt(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        by_name = {s.name: s for s in result.scenarios}
        assert by_name["Gravel"].tire_cost_usd_per_year > by_name["Asphalt"].tire_cost_usd_per_year

    def test_gravel_maintenance_exceeds_asphalt(
        self, three_surface_scenarios: list[RoadScenario]
    ) -> None:
        result = compare_scenarios(three_surface_scenarios)
        by_name = {s.name: s for s in result.scenarios}
        assert (
            by_name["Gravel"].maintenance_cost_usd_per_year
            > by_name["Asphalt"].maintenance_cost_usd_per_year
        )

    def test_result_count_matches_input(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        assert len(result.scenarios) == len(three_surface_scenarios)

    def test_scenario_names_preserved(self, three_surface_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(three_surface_scenarios)
        names = [s.name for s in result.scenarios]
        assert names == ["Asphalt", "Gravel", "Concrete"]

    def test_distance_scaling(self) -> None:
        """Doubling haul distance exactly doubles all annual costs."""
        base = [
            RoadScenario(
                name="A",
                surface="asphalt",
                thickness_mm=100,
                haul_distance_km=5.0,
                trips_per_day=20,
            )
        ]
        double = [
            RoadScenario(
                name="A",
                surface="asphalt",
                thickness_mm=100,
                haul_distance_km=10.0,
                trips_per_day=20,
            )
        ]
        r_base = compare_scenarios(base)
        r_double = compare_scenarios(double)
        s0 = r_base.scenarios[0]
        s1 = r_double.scenarios[0]
        import math

        assert math.isclose(s1.fuel_cost_usd_per_year, s0.fuel_cost_usd_per_year * 2, rel_tol=1e-9)
        assert math.isclose(s1.tire_cost_usd_per_year, s0.tire_cost_usd_per_year * 2, rel_tol=1e-9)
        assert math.isclose(
            s1.maintenance_cost_usd_per_year, s0.maintenance_cost_usd_per_year * 2, rel_tol=1e-9
        )
