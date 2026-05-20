# HaulPave

> Open-source pavement structure and operating-cost analysis toolkit for mine haul roads.

HaulPave is a Python library for designing pavement structures on mine haul roads
and estimating operating-cost impacts.

## Status

HaulPave v0.3.0 is released and available on PyPI. See the [project roadmap](https://github.com/rachmad-jenss/haul-pave)
for upcoming releases.

| Phase | Status |
|-------|--------|
| Phase 0 — Benchmark Foundation | ✅ Complete |
| Phase 1 — MVP (v0.1.0) | ✅ Complete |
| Phase 2 — TRH 14 (v0.2.0) | ✅ Complete |
| Phase 3 — Economics (v0.3.0) | ✅ Complete |
| Phase 4 — Documentation, Examples & v1.0.0 | 🔄 In Progress |

## Installation

```bash
pip install haulpave
```

## Quick Start

```python
from haulpave.traffic.cesa import compute_cesa
from haulpave.traffic.coverages import compute_coverages
from haulpave.pavement import design_pavement
from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec

# Define a haul truck
tire = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=5200.0)
truck = MiningVehicle(
    name="CAT 777G",
    gross_vehicle_mass_t=186.0,
    axle_groups=[
        AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=155.0, tire_spec=tire),
        AxleGroup(axle_count=2, tyres_per_axle=4, gross_load_kn=760.0, tire_spec=tire),
    ],
    source="Caterpillar 777G spec sheet, 2023",
)

# Configure traffic
traffic = TrafficInput(
    fleet=[FleetUnit(vehicle=truck, trips_per_day=50)],
    design_life_years=10,
    working_days_per_year=350,
)

# Compute CESA and coverages
cesa = compute_cesa(traffic)
coverages = compute_coverages(traffic)
print(f"CESA: {cesa.total_cesa:.0f}")
print(f"Coverages: {coverages.total_coverages:.0f}")

# Design pavement thickness (USACE CBR method)
design = design_pavement(traffic, subgrade_cbr=5.0)
print(f"Required thickness: {design.required_thickness_mm:.0f} mm")
```

## Scope

HaulPave computes traffic loading (CESA + design coverages) and pavement layer
thicknesses using USACE TM 5-822-12 and TRH 14 (CSRA 1985) methods. It also
provides operating-cost and rolling-resistance scenario comparison. It does
**not** cover geometric design, drainage, berm design, or traffic operations.
See [SCOPE.md](https://github.com/rachmad-jenss/haul-pave/blob/main/SCOPE.md).

## License

MIT
