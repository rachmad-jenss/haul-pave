# Pavement Module

Module: `src/haulpave/pavement/`

Pavement thickness design engines — USACE TM 5-822-12 CBR method and
TRH 14 (CSRA 1985) method, plus a side-by-side comparison engine.

---

## `design_pavement(traffic: TrafficInput, subgrade_cbr: float, curve_id: str = "usace_cbr_v1") -> PavementResult`

Design pavement thickness using the USACE TM 5-822-12 CBR method.
Pipeline: CESA → design coverages → CBR curve interpolation (PCHIP).

**Source:** `src/haulpave/pavement/__init__.py:69`

| Parameter | Type | Description |
|-----------|------|-------------|
| `traffic` | `TrafficInput` | Fleet mix, design life, and working days |
| `subgrade_cbr` | `float` | Subgrade CBR [%] |
| `curve_id` | `str` | Digitized curve dataset identifier, e.g. `"usace_cbr_v1"` |

**Returns:** `PavementResult`

---

## `PavementResult`

```python
@dataclass(frozen=True)
class PavementResult:
    total_cesa: float
    total_coverages: float
    required_thickness_mm: float
    design_wheel_load_kn: float
    method: str = "USACE TM 5-822-12 CBR design curves + AASHTO 4th-power LEF"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"]
```

**Source:** `src/haulpave/pavement/__init__.py:40`

| Attribute | Description |
|-----------|-------------|
| `total_cesa` | Cumulative Equivalent Standard Axles over the full design life |
| `total_coverages` | Total equivalent design-wheel coverages over the full design life |
| `required_thickness_mm` | Required total pavement thickness from the CBR design curve [mm] |
| `design_wheel_load_kn` | Maximum single-wheel load in the fleet [kN] |
| `method` | Human-readable method identifier |
| `confidence` | Confidence label per project plan §4.3 |

---

## `cbr_thickness_from_coverages(subgrade_cbr: float, design_coverages: float, curve_id: str = "usace_cbr_v1") -> float`

Return required CBR pavement thickness from pre-computed design coverages.
Skips the CESA/coverages pipeline. Intended for the haul-calc JSON-RPC bridge.

**Source:** `src/haulpave/pavement/__init__.py:128`

---

## `trh14_thickness_from_coverages(subgrade_cbr: float, design_coverages: float) -> TRH14Result`

Return TRH 14 pavement thickness from subgrade CBR and pre-computed coverages.
Adapter for the haul-calc JSON-RPC bridge.

**Source:** `src/haulpave/pavement/__init__.py:158`

---

## `compute_trh14(traffic: TrafficInput, subgrade_cbr: float) -> TRH14Result`

Design pavement thickness using the TRH 14 (CSRA 1985) method.
Pipeline: design coverages → CBR-to-G-class → TRH 14 catalog lookup
(log-linear interpolation on coverages axis).

**Source:** `src/haulpave/pavement/trh14.py:191`

| Parameter | Type | Description |
|-----------|------|-------------|
| `traffic` | `TrafficInput` | Fleet mix, design life, and working days |
| `subgrade_cbr` | `float` | Subgrade CBR [%] |

**Returns:** `TRH14Result`

---

## `TRH14Result`

```python
@dataclass(frozen=True)
class TRH14Result:
    material_class: str
    total_thickness_mm: float
    total_coverages: float
    design_wheel_load_kn: float
    method: str = "TRH 14 (CSRA 1985) design catalog + USACE design-coverages"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"]
```

**Source:** `src/haulpave/pavement/trh14.py:161`

| Attribute | Description |
|-----------|-------------|
| `material_class` | TRH 14 G-class of the subgrade, e.g. `"G5"` |
| `total_thickness_mm` | Required total compacted pavement thickness [mm] |
| `total_coverages` | Total equivalent design-wheel coverages (USACE method) |
| `design_wheel_load_kn` | Maximum single-wheel load in the fleet [kN] |
| `method` | Human-readable method identifier |
| `confidence` | Confidence label per project plan §4.3 |

---

## `cbr_to_material_class(cbr: float) -> str`

Map subgrade CBR [%] to TRH 14 G-class material classification.
Boundaries follow TRH 14 Table 2 (inclusive on the lower bound).

**Source:** `src/haulpave/pavement/trh14.py:57`

---

## `compare_methods(traffic: TrafficInput, subgrade_cbr: float, curve_id: str = "usace_cbr_v1") -> ComparisonResult`

Compare USACE TM 5-822-12 CBR and TRH 14 pavement design results side-by-side.
Returns a `ComparisonResult` including the thickness delta.

**Source:** `src/haulpave/pavement/compare.py:74`

---

## `ComparisonResult`

```python
@dataclass(frozen=True)
class ComparisonResult:
    usace: PavementResult
    trh14: TRH14Result
    delta_mm: float
    subgrade_cbr: float
    curve_id: str
    method: str = "USACE TM 5-822-12 CBR vs TRH 14 (CSRA 1985) comparison"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"]
```

**Source:** `src/haulpave/pavement/compare.py:39`

| Attribute | Description |
|-----------|-------------|
| `usace` | Full result from the USACE CBR design path |
| `trh14` | Full result from the TRH 14 design catalog path |
| `delta_mm` | Thickness difference: TRH14 − USACE [mm] |
| `subgrade_cbr` | Subgrade CBR [%] used for both calculations |
| `curve_id` | USACE CBR curve dataset identifier |
| `method` | Human-readable method identifier |
| `confidence` | Confidence label (inherits `benchmark_tested` from sub-engines) |
