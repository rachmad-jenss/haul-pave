# Utilities Module

Module: `src/haulpave/utils/`

Interpolation utilities for empirical curve data used in pavement thickness
design.

---

## `load_curve_data(curve_id: str) -> dict[str, Any]`

Load digitized curve JSON by curve identifier from the curves directory
(`src/haulpave/design/curves/`).

**Source:** `src/haulpave/utils/interpolation.py:16`

| Parameter | Description |
|-----------|-------------|
| `curve_id` | Curve dataset identifier, e.g. `"usace_cbr_v1"` |

**Returns:** Dictionary with `cbr_values`, `coverage_levels`, and `thickness_mm` keys.

---

## `interpolate_thickness(curve_data: dict[str, Any], cbr: float, coverages: float) -> float`

Interpolate required pavement thickness for given CBR and design coverages
using 2-step PCHIP interpolation:

1. Interpolate thickness vs CBR at each coverage level.
2. Log-linear interpolation between coverage levels.

**Source:** `src/haulpave/utils/interpolation.py:58`

| Parameter | Type | Description |
|-----------|------|-------------|
| `curve_data` | `dict[str, Any]` | Loaded curve JSON (from `load_curve_data`) |
| `cbr` | `float` | Subgrade CBR [%], must be within curve range |
| `coverages` | `float` | Design coverages, must be > 0 |

**Returns:** Required total pavement thickness [mm].

**Raises:** `ValueError` if CBR is outside the supported range, coverages ≤ 0,
or curve data is malformed.
