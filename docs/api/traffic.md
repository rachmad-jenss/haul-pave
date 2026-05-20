# Traffic Module

Module: `src/haulpave/traffic/`

CESA and design-coverages calculation engines for mine haul road traffic loading.

---

## `compute_cesa(traffic: TrafficInput) -> CesaResult`

Compute Cumulative Equivalent Standard Axles using the AASHTO (1993) 4th-power
Load Equivalency Factor (LEF) method.

**Source:** `src/haulpave/traffic/cesa.py:88`

| Parameter | Type | Description |
|-----------|------|-------------|
| `traffic` | `TrafficInput` | Fleet mix, design life, and working days per year |

**Returns:** `CesaResult` — frozen dataclass with `total_cesa`, `method`, and `confidence`.

---

## `CesaResult`

```python
@dataclass(frozen=True)
class CesaResult:
    total_cesa: float
    method: str = "AASHTO 4th-power LEF (AASHTO 1993)"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"]
```

**Source:** `src/haulpave/traffic/cesa.py:45`

| Attribute | Description |
|-----------|-------------|
| `total_cesa` | Cumulative Equivalent Standard Axles over the full design life |
| `method` | Human-readable method identifier |
| `confidence` | Confidence label per project plan §4.3 |

---

## `compute_coverages(traffic: TrafficInput) -> CoveragesResult`

Compute design coverages using the USACE TM 5-822-12 pass-count method.
The design wheel load is the heaviest single-wheel load in the fleet; all other
vehicles are weighted by the 4th power of the wheel-load ratio.

**Source:** `src/haulpave/traffic/coverages.py:152`

| Parameter | Type | Description |
|-----------|------|-------------|
| `traffic` | `TrafficInput` | Fleet mix, design life, and working days per year |

**Returns:** `CoveragesResult` — frozen dataclass with `total_coverages`,
`design_wheel_load_kn`, `method`, and `confidence`.

---

## `CoveragesResult`

```python
@dataclass(frozen=True)
class CoveragesResult:
    total_coverages: float
    design_wheel_load_kn: float
    method: str = "USACE TM 5-822-12 pass-count method"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"]
```

**Source:** `src/haulpave/traffic/coverages.py:51`

| Attribute | Description |
|-----------|-------------|
| `total_coverages` | Total equivalent design-wheel coverages over the full design life |
| `design_wheel_load_kn` | Maximum single-wheel load in the fleet [kN] — the design vehicle |
| `method` | Human-readable method identifier |
| `confidence` | Confidence label per project plan §4.3 |
