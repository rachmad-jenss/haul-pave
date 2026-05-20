# Curve Encoding Policy

Several HaulPave design methods rely on graphical empirical curves rather than
closed-form equations. Because digitisation introduces its own uncertainty,
all encoded curves must comply with this policy.

## Policy Overview

| Requirement | Detail |
|:------------|:--------|
| **Source documentation** | Exact document, edition/year, page number, and figure/table number |
| **Digitisation method** | Tool or method stated (e.g., WebPlotDigitizer 4.6, manual point extraction) |
| **Stored representation** | Versioned JSON files of (x, y) control points |
| **Companion metadata** | YAML file with full provenance (`.meta.yaml`) |
| **Interpolation** | PCHIP default (`scipy.interpolate.PchipInterpolator`) |
| **Tolerance** | Documented per curve (typically ±5 mm or ±10 %, whichever is greater) |
| **Versioning** | Bump suffix on re-digitisation; previous versions retained |

## Digitisation Policy

Every encoded curve must satisfy these requirements:

1. **Source documentation** — cite the exact source figure including document
   title, edition/year, page number, and figure/table number.

2. **Digitisation method** — record the tool or method used (e.g.,
   WebPlotDigitizer 4.6, manual point extraction at standard knot intervals).
   Control points must be extracted at sufficient density to capture all
   curvature changes without aliasing.

3. **Stored representation** — digitised curves are stored as versioned JSON
   files in `src/haulpave/design/curves/`:
   ```
   src/haulpave/design/curves/
   ├── <name>_v<N>.json          # Control point data
   ├── <name>_v<N>.meta.yaml     # Provenance metadata
   ```

4. **Companion metadata** — every JSON file must have a `.meta.yaml` file with:
   - `curve_id`: unique identifier matching the JSON filename
   - `version`: semantic version string
   - `source_document`: full citation of the source
   - `figure`: exact figure/table reference
   - `digitization_method`: tool and approach used
   - `digitization_date`: ISO date of digitisation
   - `digitized_by`: person or team who performed the digitisation
   - `tolerance_mm`: expected absolute tolerance in mm
   - `notes`: usage constraints, range limits, special handling
   - `license`: source document copyright or public domain status

5. **Interpolation method** — monotonic cubic spline
   (`scipy.interpolate.PchipInterpolator`) is the default. The method is
   recorded in the curve metadata and may be overridden if a different method
   better fits the curve's behaviour.

6. **Tolerance** — benchmark expected values are pinned to a specific curve
   version. Acceptable deviation between HaulPave's interpolated result and a
   hand-read value from the original chart is documented per curve (typically
   ±5 mm or ±10 %, whichever is greater).

## Interpolation: PCHIP

HaulPave uses **Piecewise Cubic Hermite Interpolating Polynomial** (PCHIP)
via `scipy.interpolate.PchipInterpolator` as the default interpolation method.

Properties of PCHIP:
- **Monotonicity-preserving** — will not overshoot between data points,
  which is critical for design curves where physical relationships (e.g.,
  higher CBR → less thickness) must be maintained.
- **C¹ continuous** — first derivative is continuous, producing smooth
  transitions between segments.
- **Localised response** — changes in one region of the curve do not
  propagate unphysically to distant regions.

For the CBR thickness curves (`usace_cbr_v1`), interpolation proceeds in
two steps:

1. **CBR interpolation**: at each discrete coverage level, a PCHIP spline
   is fitted over (`cbr_values`, `thickness_mm`). Thickness at the
   requested CBR is evaluated from this spline.

2. **Coverage interpolation**: the thickness values from step 1 are plotted
   against log-transformed coverage levels. A second PCHIP spline over
   `(log10(coverage), thickness)` yields the final thickness at the
   requested coverage.

Coverage values outside the curve's range are clamped to the boundary with a
warning. CBR values outside the range raise `ValueError`.

See `src/haulpave/utils/interpolation.py` for the implementation.

## Curves

### Currently Encoded

| Curve | File | Source | Status |
|:------|:-----|:-------|:-------|
| USACE CBR curves | `usace_cbr_v1.json` + `.meta.yaml` | USACE TM 5-822-12, Figure 1 | Implemented (DAS-103) |
| TRH 14 catalogue | `trh14_catalog_v1.json` | Thompson & Visser (2006), Table 3 | Catalog data added |

### Adding a New Curve

1. Digitise the source figure using a validated tool (e.g., WebPlotDigitizer).
2. Record source, figure/table number, digitisation method, and tolerance in
   the `.meta.yaml` companion file.
3. Write unit tests in `tests/test_utils/test_interpolation.py` verifying
   monotonicity and boundary behaviour.
4. Bump the version suffix (`_v2`, `_v3`) on any re-digitisation.

## Versioning

Curve data files are versioned with a `_v<N>` suffix (e.g., `usace_cbr_v1.json`).
The version number is bumped on any re-digitisation:

- **v1 → v2**: re-digitised from the same source with higher fidelity
- **v1 → v2**: digitised from a newer edition of the source document
- Previous versions are retained in the repository for reproducibility.
- Benchmarks reference a specific curve version via `load_curve_data("usace_cbr_v1")`.

## Source Attribution

All curve metadata must include the `source_document` field with a complete
citation that allows an independent engineer to locate the original figure.
Where the source document is in the public domain (e.g., US Government
publications), note this in the `license` field. For copyrighted sources,
include the copyright holder and permissions status.

This policy is defined in the HaulPave Project Plan (Section 4.5) and is
mandatory for all curve data committed to this repository.
