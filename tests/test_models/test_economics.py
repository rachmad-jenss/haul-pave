"""Tests for haulpave.models.economics."""

import pytest
from pydantic import ValidationError

from haulpave.models.economics import CostAssumptions, CostScenario, EconomicResult


@pytest.fixture()
def assumptions() -> CostAssumptions:
    return CostAssumptions(
        fuel_cost_per_litre=1.80,
        tyre_cost_per_hour=45.0,
        maintenance_cost_per_km=2.50,
        operator_cost_per_hour=55.0,
    )


@pytest.fixture()
def scenario(assumptions: CostAssumptions) -> CostScenario:
    return CostScenario(
        scenario_id="baseline",
        haul_distance_km=3.5,
        average_speed_kmh=25.0,
        payload_t=220.0,
        fuel_consumption_l_per_km=5.2,
        assumptions=assumptions,
    )


class TestCostAssumptions:
    def test_valid(self, assumptions: CostAssumptions) -> None:
        assert assumptions.currency == "USD"
        assert assumptions.fuel_cost_per_litre == pytest.approx(1.80)

    def test_zero_fuel_cost_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CostAssumptions(
                fuel_cost_per_litre=0.0,
                tyre_cost_per_hour=10.0,
                maintenance_cost_per_km=1.0,
                operator_cost_per_hour=20.0,
            )

    def test_negative_maintenance_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CostAssumptions(
                fuel_cost_per_litre=1.0,
                tyre_cost_per_hour=10.0,
                maintenance_cost_per_km=-1.0,
                operator_cost_per_hour=20.0,
            )

    def test_invalid_currency_pattern_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CostAssumptions(
                fuel_cost_per_litre=1.0,
                tyre_cost_per_hour=10.0,
                maintenance_cost_per_km=1.0,
                operator_cost_per_hour=20.0,
                currency="usd",  # lowercase — must be uppercase
            )


class TestCostScenario:
    def test_valid(self, scenario: CostScenario) -> None:
        assert scenario.scenario_id == "baseline"
        assert scenario.haul_distance_km == pytest.approx(3.5)

    def test_zero_distance_rejected(self, assumptions: CostAssumptions) -> None:
        with pytest.raises(ValidationError):
            CostScenario(
                scenario_id="bad",
                haul_distance_km=0.0,
                average_speed_kmh=25.0,
                payload_t=220.0,
                fuel_consumption_l_per_km=5.2,
                assumptions=assumptions,
            )


class TestEconomicResult:
    def test_valid(self) -> None:
        er = EconomicResult(
            scenario_id="baseline",
            cost_per_tonne_km=0.85,
            cost_per_trip=520.0,
            trips_per_year=18_000.0,
            annual_cost=9_360_000.0,
            currency="USD",
        )
        assert er.method == "haulpave-economics-v1"

    def test_negative_cost_rejected(self) -> None:
        with pytest.raises(ValidationError):
            EconomicResult(
                scenario_id="bad",
                cost_per_tonne_km=-1.0,
                cost_per_trip=100.0,
                trips_per_year=1000.0,
                annual_cost=100_000.0,
                currency="USD",
            )

    def test_empty_scenario_id_rejected(self) -> None:
        with pytest.raises(ValidationError):
            EconomicResult(
                scenario_id="",
                cost_per_tonne_km=0.85,
                cost_per_trip=520.0,
                trips_per_year=18_000.0,
                annual_cost=9_360_000.0,
                currency="USD",
            )
