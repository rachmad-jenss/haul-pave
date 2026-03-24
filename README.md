# HaulPave

> Open-source pavement structure and operating-cost analysis toolkit for mine haul roads.

[![CI](https://github.com/rachmad-jenss/haul-pave/actions/workflows/ci.yml/badge.svg)](https://github.com/rachmad-jenss/haul-pave/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What HaulPave Does

- Computes traffic loading (CESA and design coverages) from a mining fleet composition.
- Determines pavement layer thicknesses using established empirical methods (USACE CBR-based, TRH 14).
- Estimates comparative operating costs (tire, fuel, maintenance) across design scenarios.
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

*Full examples available after v0.1.0 release (Phase 1).*

## Status

| Phase | Status | Target |
|-------|--------|--------|
| Phase 0 — Benchmark Foundation | 🔄 In Progress | 2026-Q2 |
| Phase 1 — MVP (CESA + CBR thickness) | ⏳ Planned | 2026-Q2 |
| Phase 2 — TRH 14 + comparison engine | ⏳ Planned | 2026-Q3 |
| Phase 3 — Economics scenario calculator | ⏳ Planned | 2026-Q3 |
| Phase 4 — Docs + community | ⏳ Planned | 2026-Q4 |

## Design Principles

- **Benchmark-first**: every calculation method is tested against hand-computed examples
  before any engine code is written.
- **Honest documentation**: explicit assumptions, limitations, and method references.
- **SI units internally**: mm, km, kN, kPa, tonnes — no implicit unit mixing.
- **Open-source hygiene**: no proprietary data redistribution; OEM data requires source attribution.

## License

MIT — see [LICENSE](LICENSE).
