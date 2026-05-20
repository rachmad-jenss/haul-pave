"""Unit tests for economics.compare — compare_scenarios."""

from __future__ import annotations

import pytest

from haulpave.economics.compare import ComparisonResult, RoadScenario, compare_scenarios


@pytest.fixture()
def two_scenarios() -> list[RoadScenario]:
    return [
        RoadScenario(
            name="Asphalt",
            surface="asphalt",
            haul_distance_km=5.0,
            trips_per_day=20,
        ),
        RoadScenario(
            name="Gravel",
            surface="gravel",
            haul_distance_km=5.0,
            trips_per_day=20,
        ),
    ]


class TestCompareScenarios:
    def test_returns_comparison_result(self, two_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(two_scenarios)
        assert isinstance(result, ComparisonResult)
        assert len(result.scenarios) == 2

    def test_gravel_more_expensive_than_asphalt(self, two_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(two_scenarios)
        asphalt = result.scenarios[0]
        gravel = result.scenarios[1]
        assert gravel.fuel_cost_usd_per_year > asphalt.fuel_cost_usd_per_year
        assert gravel.tire_cost_usd_per_year > asphalt.tire_cost_usd_per_year
        assert gravel.maintenance_cost_usd_per_year > asphalt.maintenance_cost_usd_per_year

    def test_all_costs_positive(self, two_scenarios: list[RoadScenario]) -> None:
        result = compare_scenarios(two_scenarios)
        for s in result.scenarios:
            assert s.fuel_cost_usd_per_year > 0
            assert s.tire_cost_usd_per_year > 0
            assert s.maintenance_cost_usd_per_year > 0

    def test_invalid_working_days_raises(self, two_scenarios: list[RoadScenario]) -> None:
        with pytest.raises(ValueError, match="working_days_per_year"):
            compare_scenarios(two_scenarios, working_days_per_year=0)

    def test_invalid_fuel_price_raises(self, two_scenarios: list[RoadScenario]) -> None:
        with pytest.raises(ValueError, match="fuel_price"):
            compare_scenarios(two_scenarios, fuel_price_usd_per_litre=0)

    def test_empty_scenarios(self) -> None:
        result = compare_scenarios([])
        assert result.scenarios == []

    def test_concrete_cheapest(self) -> None:
        scenarios = [
            RoadScenario(name="A", surface="asphalt", haul_distance_km=10, trips_per_day=10),
            RoadScenario(name="G", surface="gravel", haul_distance_km=10, trips_per_day=10),
            RoadScenario(
                name="C",
                surface="concrete",
                haul_distance_km=10,
                trips_per_day=10,
            ),
        ]
        result = compare_scenarios(scenarios)
        by_name = {s.name: s for s in result.scenarios}
        assert by_name["C"].fuel_cost_usd_per_year < by_name["A"].fuel_cost_usd_per_year
        assert by_name["C"].tire_cost_usd_per_year < by_name["A"].tire_cost_usd_per_year
