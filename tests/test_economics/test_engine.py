"""Tests for haulpave.economics.engine — compute_economics."""

from __future__ import annotations

import pytest

from haulpave.economics.engine import EconomicsResult, compute_economics, to_economic_result
from haulpave.models.economics import CostAssumptions, CostScenario, EconomicResult


@pytest.fixture()
def assumptions() -> CostAssumptions:
    return CostAssumptions(
        fuel_cost_per_litre=1.50,
        tyre_cost_per_hour=25.0,
        maintenance_cost_per_km=3.0,
        operator_cost_per_hour=40.0,
        currency="USD",
    )


@pytest.fixture()
def scenario(assumptions: CostAssumptions) -> CostScenario:
    return CostScenario(
        scenario_id="test-01",
        haul_distance_km=5.0,
        average_speed_kmh=25.0,
        payload_t=150.0,
        fuel_consumption_l_per_km=2.0,
        assumptions=assumptions,
    )


class TestComputeEconomics:
    def test_returns_economics_result(self, scenario: CostScenario) -> None:
        result = compute_economics(scenario)
        assert isinstance(result, EconomicsResult)

    def test_cost_breakdown_correct(self, scenario: CostScenario) -> None:
        """Hand-calc: distance=5km, speed=25km/h, trip_time=0.2h."""
        result = compute_economics(scenario)
        # fuel: 2.0 * 5.0 * 1.50 = 15.0
        assert result.fuel_cost_per_trip == pytest.approx(15.0)
        # tyre: 25.0 * 0.2 = 5.0
        assert result.tyre_cost_per_trip == pytest.approx(5.0)
        # maintenance: 3.0 * 5.0 = 15.0
        assert result.maintenance_cost_per_trip == pytest.approx(15.0)
        # operator: 40.0 * 0.2 = 8.0
        assert result.operator_cost_per_trip == pytest.approx(8.0)

    def test_cost_per_trip_is_sum(self, scenario: CostScenario) -> None:
        result = compute_economics(scenario)
        expected = 15.0 + 5.0 + 15.0 + 8.0  # = 43.0
        assert result.cost_per_trip == pytest.approx(expected)

    def test_cost_per_tonne_km(self, scenario: CostScenario) -> None:
        result = compute_economics(scenario)
        # 43.0 / (150.0 * 5.0) = 43.0 / 750.0 ≈ 0.05733
        assert result.cost_per_tonne_km == pytest.approx(43.0 / 750.0)

    def test_no_annual_cost_without_trips(self, scenario: CostScenario) -> None:
        result = compute_economics(scenario)
        assert result.trips_per_year == 0.0
        assert result.annual_cost == 0.0

    def test_annual_cost_with_trips(self, scenario: CostScenario) -> None:
        result = compute_economics(scenario, trips_per_day=20.0, working_days_per_year=300)
        assert result.trips_per_year == pytest.approx(6000.0)
        assert result.annual_cost == pytest.approx(43.0 * 6000.0)

    def test_currency_propagated(self, scenario: CostScenario) -> None:
        result = compute_economics(scenario)
        assert result.currency == "USD"

    def test_scenario_id_propagated(self, scenario: CostScenario) -> None:
        result = compute_economics(scenario)
        assert result.scenario_id == "test-01"

    def test_confidence_is_method_implemented(self, scenario: CostScenario) -> None:
        result = compute_economics(scenario)
        assert result.confidence == "method_implemented"

    def test_result_is_frozen(self, scenario: CostScenario) -> None:
        result = compute_economics(scenario)
        with pytest.raises(AttributeError):
            result.cost_per_trip = 999.0  # type: ignore[misc]


class TestToEconomicResult:
    def test_converts_to_pydantic_model(self, scenario: CostScenario) -> None:
        result = compute_economics(scenario, trips_per_day=10.0)
        pydantic_result = to_economic_result(result)
        assert isinstance(pydantic_result, EconomicResult)
        assert pydantic_result.scenario_id == result.scenario_id
        assert pydantic_result.cost_per_trip == pytest.approx(result.cost_per_trip)
        assert pydantic_result.cost_per_tonne_km == pytest.approx(result.cost_per_tonne_km)
        assert pydantic_result.currency == result.currency
