# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
HaulPave uses [Semantic Versioning](https://semver.org/).

---

## [0.5.0] — 2026-05-21

### Added
- **USACE CBR curve extrapolation**: Coverage levels up to 1,000,000 via log-linear extrapolation. `interpolate_thickness()` returns `was_extrapolated` flag; `design_pavement()` sets `confidence="medium"` in extrapolated zone (DAS-87)
- **Custom pavement materials**: `CustomMaterial` frozen dataclass + `material_to_layer_coefficient()` for AASHTO structural number estimation. `custom_materials` parameter added to `design_pavement()`, `cbr_thickness_from_coverages()`, `trh14_thickness_from_coverages()`, `compute_trh14()`, `compare_methods()`. `PavementResult.layers` populated when custom materials provided (DAS-88)

### Changed
- `PavementResult` gains `was_extrapolated: bool` field
- `interpolate_thickness()` return type extended to `tuple[float, bool, bool]` (thickness, was_clamped, was_extrapolated)
- `cbr_thickness_from_coverages()` accepts coverages > 100,000 without clamping

### Technical
- 409 unit + benchmark tests, 92% coverage
- All CI quality checks pass (ruff, mypy, pytest)

## [0.4.1] — 2026-05-20

### Added
- **CLI commands** (`haulpave.cli.main`): `economics`, `scenario`, `export` — operating cost, rolling-resistance comparison, and Excel export from the command line (DAS-76)
- **Sensitivity analysis** (`haulpave.analysis.sensitivity`): `analyze_sensitivity()` — perturb CBR, coverages, or design life ±range_pct%, returns thickness impact (DAS-77)
- **Unit conversion** (`haulpave.utils.units`): 18 imperial↔SI conversion functions with NIST-exact factors — psi↔kPa, tons↔tonnes, inches↔mm, mph↔km/h, etc. (DAS-78)
- **Report input hash**: SHA-256 audit trail in `DesignSummary.input_hash` + `compute_input_hash()` helper (DAS-79)

### Changed
- `RoadScenario.thickness_mm` removed — field was accepted but never used in calculations (DAS-80)

### Technical
- 340+ unit + benchmark tests, ~98% coverage
- 100% coverage on all new modules (material_library, cli, analysis, utils.units, reporting)

## [0.4.0] — 2026-05-20

### Added
- Confidence label alignment (`high`/`medium`/`low` for all results)
- `PavementResult` fields: `total_thickness_mm`, `subgrade_cbr`, `layers`, `was_clamped`
- TRH14 public API export from `haulpave.pavement`
- Clamping feedback (`was_clamped` flag) on all design results

### Technical
- API refinements for haul-calc compatibility (DAS-73)
- 294+ unit tests, 97% coverage

### Added
- **Vehicle registry** (`haulpave.vehicle_registry`): `list_all()`, `find_by_id()` with 4 OEM mining trucks — CAT 797F (6104 kN), KOM 960E (5925 kN), CAT 789D (3304 kN), CAT 785D (2641 kN). Axle loads follow 25/75 front/rear split per CAT Performance Handbook Ed. 47 (DAS-267)
- **Economics compare** (`haulpave.economics.compare_scenarios`): rolling-resistance linear cost model for tire, fuel, and maintenance cost per year across `asphalt`, `gravel`, and `concrete` surfaces. Physics-verified ordering: gravel > asphalt > concrete for all cost categories. Benchmark 06 added (DAS-268)
- **Reporting summary** (`haulpave.reporting.build_design_summary`): versioned design summary envelope with UTC timestamp, package version, inputs dict, and results dict (DAS-269)
- **Pavement bridge adapters**: `cbr_thickness_from_coverages()` and `trh14_thickness_from_coverages()` — bypass `TrafficInput` pipeline for callers that already have design coverages

### Technical
- 269 unit + benchmark tests, 98.39% coverage
- `ConfidenceLabel` type added to `ScenarioComparison` and `ComparisonResult` — all new results carry `experimental` label
- Benchmark 06 reference data: hand-calculated at 10 km, 40 trips/day, 250 days/yr; tolerance 0.1%

---

## [0.2.0] — 2026-03-25

### Added
- Phase 2: Benchmark 05 — TRH 14 hand-calc, CBR-to-G-class mapping and thickness design (DAS-111)
- Phase 2: TRH 14 pavement design engine — `haulpave.pavement.trh14.compute_trh14`, `cbr_to_material_class`, G1–G7 design catalog with log-linear interpolation (DAS-112)
- Phase 2: Comparison engine — `haulpave.pavement.compare_methods` runs USACE CBR and TRH 14 side-by-side, exposes `ComparisonResult` with `delta_mm` (DAS-113)

### Technical
- All 5 benchmark test files pass with no skips (bench_01–bench_05)
- 206 unit tests, 97.97% coverage (as of 2026-03-25)
- TRH 14 design catalog digitized from Thompson & Visser (2006), G1–G7, confidence `benchmark_tested`
- Comparison engine verifies delta arithmetic: for Fleet D + CBR=12% (G5), delta = −31.8 mm (USACE more conservative)

---

## [0.1.0] — 2026-03-25

### Added
- Phase 0: Project scaffolding — pyproject.toml, package structure, pre-commit hooks (DAS-97)
- Phase 0: Pydantic data models — Vehicle, Traffic, Material, Pavement, Economics (DAS-98)
- Phase 0: Benchmark 01 — CESA hand-calc, 3 fleet compositions (DAS-99)
- Phase 0: Benchmark 02 — Coverages hand-calc, USACE pass counts (DAS-100)
- Phase 0: Digitize USACE CBR design curves + interpolation utility (DAS-103)
- Phase 0: Benchmark dossier documentation — README, sources.md, conftest.py (DAS-104)
- Phase 1: CESA engine — `haulpave.traffic.cesa.compute_cesa` AASHTO 4th-power LEF (DAS-106)
- Phase 1: Coverages engine — `haulpave.traffic.coverages.compute_coverages` USACE TM 5-822-12 (DAS-107)
- Phase 1: Pavement design engine — `haulpave.pavement.design_pavement` CBR thickness (DAS-108)

### Technical
- All 4 benchmark test files pass with no skips (as of 2026-03-25)
- 144 unit tests, 98.5% coverage (as of 2026-03-25)
- Python 3.10+ compatible, tested on 3.10, 3.11, 3.12
- SI units throughout (mm, kN, tonnes)
- Confidence labels: all engines are `benchmark_tested`
