# Reporting Module

Module: `src/haulpave/reporting/`

Versioned design summaries — wraps arbitrary design inputs and results in
a metadata envelope for reproducibility.

---

## `build_design_summary(inputs: dict[str, Any], results: dict[str, Any] | None = None, title: str = "Haul Road Pavement Design Summary") -> DesignSummary`

Build a versioned design summary from inputs and optional computed results.

**Source:** `src/haulpave/reporting/summary.py:32`

| Parameter | Type | Description |
|-----------|------|-------------|
| `inputs` | `dict[str, Any]` | Arbitrary design inputs (fleet spec, pavement params, etc.) |
| `results` | `dict[str, Any] \| None` | Computed outputs keyed by method name |
| `title` | `str` | Human-readable summary title |

**Returns:** `DesignSummary`

---

## `DesignSummary`

```python
class DesignSummary(BaseModel, frozen=True):
    title: str                        # Summary title
    generated_at: str                 # ISO 8601 UTC timestamp of generation
    package_version: str              # haul pave package version string
    inputs: dict[str, Any]           # Design inputs as passed by the caller
    results: dict[str, Any]          # Computed results keyed by method name
```

**Source:** `src/haulpave/reporting/summary.py:20`
