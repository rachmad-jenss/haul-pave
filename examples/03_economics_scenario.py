"""Example 03: Economics Scenario — Operating Cost & Rolling Resistance.

Demonstrates two economics calculations:
1. Unit-cost economics: fleet definition -> cost per trip, cost per tonne-km
2. Rolling resistance scenario comparison: asphalt vs gravel vs concrete surfaces

Run: python examples/03_economics_scenario.py
"""

from haulpave.economics.compare import RoadScenario, compare_scenarios
from haulpave.economics.engine import compute_economics as compute_operating_cost
from haulpave.models.economics import CostAssumptions, CostScenario


def main() -> None:
    print("=" * 72)
    print("EXAMPLE 03: Economics — Operating Cost & Rolling Resistance")
    print("=" * 72)

    print("\n--- Part 1: Unit-Cost Operating Cost ---")
    assumptions = CostAssumptions(
        fuel_cost_per_litre=0.80,
        tyre_cost_per_hour=45.0,
        maintenance_cost_per_km=0.35,
        operator_cost_per_hour=38.0,
        currency="USD",
    )

    scenario = CostScenario(
        scenario_id="haul_road_main",
        haul_distance_km=5.0,
        average_speed_kmh=35.0,
        payload_t=150.0,
        fuel_consumption_l_per_km=2.5,
        assumptions=assumptions,
    )

    econ = compute_operating_cost(scenario, trips_per_day=40.0, working_days_per_year=250)

    print(f"  Scenario:           {econ.scenario_id}")
    print(f"  Cost per trip:      ${econ.cost_per_trip:,.2f}")
    print(f"  Cost per tonne-km:  ${econ.cost_per_tonne_km:.4f}")
    print("  Breakdown (per trip):")
    print(f"    Fuel:             ${econ.fuel_cost_per_trip:,.2f}")
    print(f"    Tyre:             ${econ.tyre_cost_per_trip:,.2f}")
    print(f"    Maintenance:      ${econ.maintenance_cost_per_trip:,.2f}")
    print(f"    Operator:         ${econ.operator_cost_per_trip:,.2f}")
    print(f"  Annual cost:        ${econ.annual_cost:,.2f}")
    print(f"  Trips per year:     {econ.trips_per_year:,.0f}")
    print(f"  Currency:           {econ.currency}")
    print(f"  Confidence:         {econ.confidence}")

    print("\n--- Part 2: Rolling Resistance Scenario Comparison ---")

    roads = [
        RoadScenario(
            name="Asphalt",
            surface="asphalt",
            haul_distance_km=5.0,
            trips_per_day=40.0,
        ),
        RoadScenario(
            name="Gravel",
            surface="gravel",
            haul_distance_km=5.0,
            trips_per_day=40.0,
        ),
        RoadScenario(
            name="Concrete",
            surface="concrete",
            haul_distance_km=5.0,
            trips_per_day=40.0,
        ),
    ]

    comp = compare_scenarios(
        roads,
        fuel_price_usd_per_litre=0.80,
        working_days_per_year=250,
    )

    print(
        f"{'Surface':>10}  {'Fuel ($/yr)':>14}  {'Tyres ($/yr)':>14}"
        f"  {'Maint ($/yr)':>14}  {'Total ($/yr)':>14}"
    )
    print(f"{'-'*10}  {'-'*14}  {'-'*14}  {'-'*14}  {'-'*14}")

    for sc in comp.scenarios:
        total = (
            sc.fuel_cost_usd_per_year
            + sc.tire_cost_usd_per_year
            + sc.maintenance_cost_usd_per_year
        )
        print(
            f"{sc.name:>10}  {sc.fuel_cost_usd_per_year:>14,.0f}  "
            f"{sc.tire_cost_usd_per_year:>14,.0f}  "
            f"{sc.maintenance_cost_usd_per_year:>14,.0f}  "
            f"{total:>14,.0f}"
        )

    print(f"\n  Method:     {comp.method}")
    print(f"  Confidence: {comp.confidence}")
    print("  (Gravel should be highest, concrete lowest)")

    print("\nExample 03 completed successfully.")


if __name__ == "__main__":
    main()
