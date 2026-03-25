# Benchmark Dossier

## Purpose

HaulPave follows a **benchmark-first development policy**: every calculation engine must be validated against at least one hand-calculated reference case before the implementation is considered complete. This directory is the authoritative dossier of those reference cases.

Each benchmark file:

- defines expected values derived from a published hand-calculation or authoritative source,
- is a normal pytest file that skips automatically (via `pytest.importorskip`) until the corresponding engine module is implemented,
- serves as the acceptance gate — CI will fail if a benchmark regresses.

This policy means benchmark tests are written *before* (or alongside) the engine code, never after.

---

## How to Add a New Benchmark

### Naming convention

```
bench_NN_short_description.py
```

Where `NN` is a zero-padded sequence number (e.g. `03`, `04`, …). The description should be snake_case and match the engine being tested.

### Required sections in each benchmark file

1. **Module docstring** — describe the method, the source document, and the hand-calculation scenario.
2. **`EXPECTED` constant or JSON fixture** — hard-coded expected values with full provenance (source, page/equation reference, tolerance).
3. **`pytest.importorskip`** — at module level, so the file is skipped (not failed) when the engine is not yet implemented:
   ```python
   cesa = pytest.importorskip("haulpave.traffic.cesa")
   ```
4. **At least one `test_` function** — asserts engine output against expected values using `assert_within_pct` from `tests/conftest.py`.
5. **Tolerance annotation** — each assertion must state the tolerance and its justification (e.g. rounding in source, digitization error).

### Example skeleton

```python
"""Bench NN — <Method name>.

Source: <Full citation from reference_data/sources.md>
Scenario: <Brief description of the hand-calc scenario>
"""
from __future__ import annotations
import pytest

engine = pytest.importorskip("haulpave.<module>.<submodule>")

from tests.conftest import assert_within_pct  # noqa: E402

EXPECTED_VALUE = 12345.6  # <unit> — Source: <doc>, Table/Eq X, tolerance ±Y%


def test_bench_nn_scenario_name() -> None:
    result = engine.calculate(...)
    assert_within_pct(result, EXPECTED_VALUE, tolerance_pct=1.0)
```

---

## Benchmark Inventory

### Bench 01 — CESA Hand Calculation (`bench_01_cesa_hand_calc.py`)

**Status:** Implemented (DAS-101)
**Engine:** `haulpave.traffic.cesa`
**Method:** AASHTO 4th power law — Equivalent Single Axle Load (ESAL)

Three fleet compositions are tested (heavy / medium / light), each with vehicles from the shared conftest fixtures. Expected values are computed from the AASHTO 4th power law applied to each axle group, summed over the design life. Source: AASHTO (1993), Section 2.

### Bench 02 — Design Coverages Hand Calculation (`bench_02_coverages_hand_calc.py`)

**Status:** Implemented (DAS-102)
**Engine:** `haulpave.traffic.coverages`
**Method:** USACE pass-count method — Design Coverages

Same three fleet compositions as Bench 01. Expected values follow the USACE TM 5-822-12 coverage definition: one coverage equals the number of passes required for each point in the wheel path to be loaded once. Source: USACE TM 5-822-12 (1987), Section 3-2.

### Bench 03 — CBR Thickness Design (pending DAS-101)

**Status:** Pending — engine not yet implemented
**Engine:** `haulpave.design.cbr_thickness` (planned)
**Method:** CBR design curves — USACE TM 5-822-12, Figure 1

Compare engine output versus the hand-calculation example from USACE TM 5-822-12. The scenario uses a known CBR value and design coverages to determine the required structural layer thickness. Tolerance target: ±5% (limited by curve digitization resolution).

### Bench 04 — Haul Road Operating Cost (pending DAS-102)

**Status:** Pending — engine not yet implemented
**Engine:** `haulpave.economics` (planned)
**Method:** Operating cost model — published mine haul road case study

Compare engine output against a published case study with known cost breakdown (fuel, tyre wear, maintenance). Tolerance target: ±10% (sensitivity to input assumptions).

---

## Running the Benchmarks

Run all benchmarks with verbose output:

```bash
pytest tests/benchmarks/ -v
```

Run a specific benchmark:

```bash
pytest tests/benchmarks/bench_01_cesa_hand_calc.py -v
```

Run all tests (unit + benchmarks) with coverage:

```bash
pytest tests/ --cov=haulpave --cov-fail-under=85 -q
```

### Expected output before engines are implemented

Benchmarks for unimplemented engines will show as **skipped**, not failed:

```
SKIPPED [1] tests/benchmarks/bench_03_cbr_thickness.py - No module named 'haulpave.design.cbr_thickness'
```

This is intentional — skips are the correct gate state until the engine module exists.

---

## Reference Sources

Full bibliographic citations for all sources used in benchmark expected values are in:

```
tests/benchmarks/reference_data/sources.md
```
