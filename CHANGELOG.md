# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
HaulPave uses [Semantic Versioning](https://semver.org/).

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
- All 4 benchmark test files pass with no skips
- 144 unit tests, 98.5% coverage
- Python 3.10+ compatible, tested on 3.10, 3.11, 3.12
- SI units throughout (mm, kN, tonnes)
- Confidence labels: all engines are `benchmark_tested`
