"""Example 02: TRH 14 vs USACE Method Comparison.

Compares pavement design thickness from two methods side-by-side
for the same traffic input at 3 different subgrade CBR values:
- USACE TM 5-822-12 CBR design curves
- TRH 14 (CSRA 1985) design catalog

Run: python examples/02_trh14_vs_usace_comparison.py
"""

from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec
from haulpave.pavement.compare import compare_methods


def main() -> None:
    print("=" * 72)
    print("EXAMPLE 02: TRH 14 vs USACE Method Comparison")
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

    traffic = TrafficInput(
        fleet=[FleetUnit(vehicle=haul_truck, trips_per_day=30.0)],
        design_life_years=10.0,
        working_days_per_year=350,
    )

    print(
        f"\nFleet: {traffic.fleet[0].vehicle.name}"
        f" @ {traffic.fleet[0].trips_per_day} trips/day"
    )
    print(
        f"Design life: {traffic.design_life_years} years,"
        f" {traffic.working_days_per_year} days/yr"
    )
    print()

    cbr_values = [3.0, 5.0, 10.0]

    print(
        f"{'CBR':>5}  {'USACE (mm)':>12}  {'TRH 14 (mm)':>12}"
        f"  {'Delta (mm)':>12}  {'G-Class':>8}"
    )
    print(f"{'-'*5}  {'-'*12}  {'-'*12}  {'-'*12}  {'-'*8}")

    for cbr in cbr_values:
        try:
            result = compare_methods(traffic, subgrade_cbr=cbr)
            usace_thk = result.usace.required_thickness_mm
            trh14_thk = result.trh14.total_thickness_mm
            delta = result.delta_mm
            g_class = result.trh14.material_class
            print(f"{cbr:5.1f}  {usace_thk:12.1f}  {trh14_thk:12.1f}  {delta:+12.1f}  {g_class:>8}")
        except ValueError as e:
            print(f"{cbr:5.1f}  {'ERROR':>12}  {'ERROR':>12}  {'ERROR':>12}  {str(e)[:20]:>8}")

    print(f"\nMethod: {compare_methods.__doc__.strip().split(chr(10))[0]}")

    cbr_result = compare_methods(traffic, subgrade_cbr=5.0)
    print("\n--- Detail at CBR 5% ---")
    print("  USACE:")
    print(f"    CESA:           {cbr_result.usace.total_cesa:,.0f}")
    print(f"    Coverages:      {cbr_result.usace.total_coverages:,.0f}")
    print(f"    Design wheel:   {cbr_result.usace.design_wheel_load_kn:.1f} kN")
    print(f"    Thickness:      {cbr_result.usace.required_thickness_mm:.1f} mm")
    print("  TRH 14:")
    print(f"    Material class: {cbr_result.trh14.material_class}")
    print(f"    Coverages:      {cbr_result.trh14.total_coverages:,.0f}")
    print(f"    Thickness:      {cbr_result.trh14.total_thickness_mm:.1f} mm")
    print(f"  Delta (TRH14 - USACE): {cbr_result.delta_mm:+.1f} mm")

    print("\nExample 02 completed successfully.")


if __name__ == "__main__":
    main()
