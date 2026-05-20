"""Example 01: Basic Pavement Design — End-to-End Pipeline.

Demonstrates the full pavement design workflow:
1. Define a truck fleet with realistic vehicle specs
2. Compute CESA (AASHTO 4th-power LEF)
3. Compute design coverages (USACE TM 5-822-12 pass-count method)
4. Design pavement thickness (USACE CBR curves)

Run: python examples/01_basic_pavement_design.py
"""

from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec
from haulpave.pavement import design_pavement
from haulpave.traffic.cesa import compute_cesa
from haulpave.traffic.coverages import compute_coverages


def main() -> None:
    print("=" * 72)
    print("EXAMPLE 01: Basic Pavement Design — End-to-End Pipeline")
    print("=" * 72)

    tire = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=5200.0)

    haul_truck = MiningVehicle(
        name="CAT 793F",
        gross_vehicle_mass_t=623.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=550.0, tire_spec=tire),
            AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=1900.0, tire_spec=tire),
        ],
        source="Caterpillar 793F spec sheet, 2023",
    )

    support_tire = TireSpec(contact_pressure_kpa=480.0, contact_area_mm2=3800.0)
    fuel_truck = MiningVehicle(
        name="Fuel Truck",
        gross_vehicle_mass_t=30.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=100.0, tire_spec=support_tire),
            AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=200.0, tire_spec=support_tire),
        ],
        source="Generic fuel truck spec",
    )

    traffic = TrafficInput(
        fleet=[
            FleetUnit(vehicle=haul_truck, trips_per_day=30.0),
            FleetUnit(vehicle=fuel_truck, trips_per_day=15.0),
        ],
        design_life_years=10.0,
        working_days_per_year=350,
    )

    print("\nFleet:")
    for fu in traffic.fleet:
        print(f"  {fu.vehicle.name}: {fu.trips_per_day} trips/day")

    cesa_result = compute_cesa(traffic)
    print("\n--- CESA (AASHTO 4th-power LEF) ---")
    print(f"  Total CESA:       {cesa_result.total_cesa:,.2f}")
    print(f"  Method:           {cesa_result.method}")
    print(f"  Confidence:       {cesa_result.confidence}")

    cov_result = compute_coverages(traffic)
    print("\n--- Design Coverages (USACE TM 5-822-12) ---")
    print(f"  Total coverages:  {cov_result.total_coverages:,.2f}")
    print(f"  Design wheel load: {cov_result.design_wheel_load_kn:.1f} kN")
    print(f"  Method:           {cov_result.method}")
    print(f"  Confidence:       {cov_result.confidence}")

    subgrade_cbr = 5.0
    print("\n--- Pavement Thickness (USACE CBR Curves) ---")
    print(f"  Subgrade CBR:     {subgrade_cbr}%")
    try:
        pv_result = design_pavement(traffic, subgrade_cbr=subgrade_cbr)
        print(f"  Required thickness: {pv_result.required_thickness_mm:.1f} mm")
        print(f"  Method:            {pv_result.method}")
        print(f"  Confidence:        {pv_result.confidence}")
    except ValueError as e:
        print(f"  ERROR: {e}")
        return

    print("\n--- Summary ---")
    print(f"  Design life:      {traffic.design_life_years} years")
    print(f"  Working days/yr:  {traffic.working_days_per_year}")
    print(f"  CESA:             {cesa_result.total_cesa:,.0f}")
    print(f"  Coverages:        {cov_result.total_coverages:,.0f}")
    print(f"  Pavement:         {pv_result.required_thickness_mm:.0f} mm @ CBR {subgrade_cbr}%")

    print("\nExample 01 completed successfully.")


if __name__ == "__main__":
    main()
