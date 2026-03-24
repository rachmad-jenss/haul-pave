# Curve Data — Encoding Policy

This directory contains digitized empirical design curves used by the HaulPave
design engines.

## Policy

All curve data files must comply with the **Curve Encoding Policy** documented in
`docs/methodology/curve-encoding.md` (added in Phase 1). Key requirements:

| Requirement        | Detail |
|--------------------|--------|
| Format             | JSON (`<name>_v<N>.json`) |
| Metadata           | Companion YAML (`<name>_v<N>.meta.yaml`) |
| Source             | Exact document, edition, figure/table number |
| Digitization method | Stated (e.g., WebPlotDigitizer 4.6) |
| Tolerance          | ±X mm or ±X% documented per curve |
| Interpolation      | PCHIP default (`scipy.interpolate.PchipInterpolator`) |
| Versioning         | Bump version number on any re-digitization |

## Files

| File | Status | Source | Implemented |
|------|--------|--------|-------------|
| `usace_cbr_v1.json` | Planned | USACE TM 5-822-12 | DAS-103 |
| `usace_cbr_v1.meta.yaml` | Planned | USACE TM 5-822-12 | DAS-103 |

## Adding New Curves

1. Digitize the source figure using a validated tool (e.g., WebPlotDigitizer).
2. Record source, figure/table number, digitization method, and tolerance in the
   `.meta.yaml` companion file.
3. Write unit tests in `tests/test_utils/test_interpolation.py` verifying
   monotonicity and boundary behaviour.
4. Bump the version suffix (`_v2`, `_v3`) on any re-digitization.
