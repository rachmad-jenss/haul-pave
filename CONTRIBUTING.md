# Contributing to HaulPave

Thank you for your interest in contributing! HaulPave is a benchmark-driven
engineering library — contribution quality standards reflect that.

*Full contributing guide added in Phase 4 (v1.0). The principles below apply immediately.*

## Core Principles

### Benchmark-First

Every new calculation method must have hand-computed benchmark cases **before**
any engine code is written. No exceptions.

### Engineering Honesty

- Cite your sources (document, edition, page/equation number).
- Document assumptions and limitations explicitly.
- Don't blend or average methods with different calibration contexts.

### SI Units

All internal computations use SI units: mm, km, kN, kPa, tonnes.
Explicit conversion helpers live in `haulpave.utils.units`.

## Development Setup

```bash
git clone https://github.com/rachmad-jenss/haul-pave.git
cd haul-pave
pip install -e ".[dev]"
pre-commit install
```

## Running Tests

```bash
pytest                          # all tests
pytest tests/benchmarks/ -v    # benchmark suite only
```

## Code Quality

```bash
ruff check src/ tests/          # lint
ruff format src/ tests/         # format
mypy src/haulpave/              # type check
```

## Opening Issues

Please include:
- Method reference (document + section/equation)
- At least one benchmark case (inputs + expected outputs)
- Units for all values
