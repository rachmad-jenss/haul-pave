# HaulPave

> Open-source pavement structure and operating-cost analysis toolkit for mine haul roads.

[![CI](https://github.com/rachmad-jenss/haul-pave/actions/workflows/ci.yml/badge.svg)](https://github.com/rachmad-jenss/haul-pave/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/haulpave.svg)](https://pypi.org/project/haulpave/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What HaulPave Does

- Computes traffic loading (CESA and design coverages) from a mining fleet composition.
- Determines pavement layer thicknesses using USACE CBR and TRH 14 empirical methods.
- Estimates comparative operating costs (tire, fuel, maintenance) across road surface scenarios.
- Generates structured design summaries with full versioning metadata.

## What HaulPave Does NOT Do

HaulPave is not a complete haul road engineering tool. It does not cover geometric
design, drainage, berm design, intersection layout, grade control, or traffic operations.
All outputs require review by a qualified engineer. See [SCOPE.md](SCOPE.md).

## Installation

```bash
pip install haulpave
```

## Quick Start

```python
from haulpave.vehicle_registry import list_all, find_by_id
from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.traffic.cesa import compute_cesa
from haulpave.pavement import cbr_thickness_from_coverages
from haulpave.economics import compare_scenarios, RoadScenario
from haulpave.reporting import build_design_summary

# 1. Pick a vehicle from the built-in registry
cat797f = find_by_id("cat-797f")  # Caterpillar 797F, 6104 kN GVW

# 2. Compute CESA from fleet
traffic = TrafficInput(
    fleet=[FleetUnit(vehicle=cat797f.vehicle, trips_per_day=30)],
    design_life_years=10,
    working_days_per_year=250,
)
result = compute_cesa(traffic)
print(f"Design CESA: {result.total_cesa:.2e}")

# 3. CBR pavement thickness
thickness_mm = cbr_thickness_from_coverages(
    subgrade_cbr=8.0,
    design_coverages=result.total_cesa,
)
print(f"Required thickness: {thickness_mm:.0f} mm")

# 4. Compare surface scenarios
scenarios = [
    RoadScenario(name="Asphalt", surface="asphalt", thickness_mm=thickness_mm,
                 haul_distance_km=10, trips_per_day=30),
    RoadScenario(name="Gravel",  surface="gravel",  thickness_mm=400,
                 haul_distance_km=10, trips_per_day=30),
]
comparison = compare_scenarios(scenarios)
for s in comparison.scenarios:
    print(f"{s.name}: fuel ${s.fuel_cost_usd_per_year:,.0f}/yr")

# 5. Build a versioned summary
summary = build_design_summary(
    inputs={"subgrade_cbr": 8.0},
    results={"thickness_mm": thickness_mm},
)
print(summary.package_version, summary.generated_at)
```

## API Overview

| Module | Key symbols |
|--------|-------------|
| `haulpave.vehicle_registry` | `list_all()`, `find_by_id(id)`, `VehicleEntry` |
| `haulpave.traffic.cesa` | `compute_cesa(TrafficInput)` → `CesaResult` |
| `haulpave.traffic.coverages` | `compute_coverages(TrafficInput)` → `CoveragesResult` |
| `haulpave.pavement` | `cbr_thickness_from_coverages()`, `trh14_thickness_from_coverages()`, `design_pavement()` |
| `haulpave.economics` | `compare_scenarios([RoadScenario])` → `ComparisonResult` |
| `haulpave.reporting` | `build_design_summary(inputs, results)` → `DesignSummary` |

## Built-in Vehicle Registry

Four OEM mining trucks with GVW and 25/75 front/rear axle-load split (CAT Performance Handbook Ed. 47):

| ID | Model | GVW (kN) |
|----|-------|----------|
| `cat-797f` | Caterpillar 797F | 6 104 |
| `kom-960e` | Komatsu 960E | 5 925 |
| `cat-789d` | Caterpillar 789D | 3 304 |
| `cat-785d` | Caterpillar 785D | 2 641 |

## Status

| Phase | Content | Status |
|-------|---------|--------|
| Phase 0 — Benchmark Foundation | Benchmarks 01–05, Pydantic models, USACE CBR curves | ✅ Done (v0.1.0) |
| Phase 1 — MVP | CESA engine, coverages engine, CBR pavement design | ✅ Done (v0.1.0) |
| Phase 2 — TRH 14 + comparison | TRH 14 engine, USACE vs TRH 14 comparison | ✅ Done (v0.2.0) |
| Phase 3 — Economics + registry | Vehicle registry, rolling-resistance cost model, design summary | ✅ Done (v0.3.0) |
| Phase 4 — Docs + community | MkDocs site, case studies, CLI polish | ⏳ Planned (2026-Q4) |

## Design Principles

- **Benchmark-first**: every calculation method is tested against hand-computed examples before engine code is written.
- **Confidence labeling**: `benchmark_tested` / `method_implemented` / `experimental` on all outputs.
- **Honest documentation**: explicit assumptions, limitations, and method references.
- **SI units internally**: mm, km, kN, kPa, tonnes — no implicit unit mixing.
- **Open-source hygiene**: no proprietary data redistribution; OEM data requires source attribution.

## License

MIT — see [LICENSE](LICENSE).
