# HaulPave — Project Plan v3

> Open-source pavement structure and operating-cost analysis toolkit for mine haul roads.

---

## 1. What This Is (and What It Isn't)

HaulPave is a Python library for designing pavement structures on mine haul roads and estimating their operating-cost impact. It is initially informed by methods and use cases common in Southeast Asian, Australian, and Sub-Saharan African open-pit mining — but the engineering methods it implements are internationally published and applicable wherever heavy-haul mine roads exist.

**What HaulPave does:**

- Computes traffic loading (CESA and design coverages) from a mining fleet composition.
- Determines pavement layer thicknesses using established empirical methods.
- Estimates comparative operating costs (tire, fuel, maintenance) across design scenarios using explicit assumptions.
- Generates structured design summaries for engineering review.

**What HaulPave is NOT:**

- Not a complete haul road engineering tool. It does not cover geometric design, drainage, berm design, intersection layout, grade control, or traffic operations.
- Not a predictive model. Economic outputs are scenario-based estimates with explicit assumptions, not high-fidelity predictions.
- Not a replacement for engineering judgment. All outputs require review by a qualified engineer familiar with site conditions.
- Not validated in the field-calibrated sense. It is benchmark-driven: every calculation is traceable to a published method and tested against hand-computed examples. But "benchmark-driven" is not "field-validated."

### Why This Matters

Mine haul roads carry 100–400 ton payload trucks, 24/7/365. Despite this, pavement design is often done with rule-of-thumb or opaque spreadsheets. The consequences are measurable:

| Impact Area           | Typical Annual Cost Penalty            | Source / Basis                  |
| --------------------- | -------------------------------------- | ------------------------------- |
| Tire wear             | USD 80,000 – 250,000 per truck         | Kaufman & Ault (1977), OEM data |
| Fuel overconsumption  | USD 40,000 – 120,000 per truck         | Thompson & Visser (2006)        |
| Maintenance (grading) | USD 15,000 – 50,000 per km/year        | Industry benchmarks             |
| Productivity loss     | 5–15% cycle time increase              | Fleet management studies        |

These figures are indicative ranges from published literature — actual values are highly site-dependent. HaulPave aims to make the analysis behind these numbers transparent and reproducible, not to promise precision that the underlying data doesn't support.

### Project Identity

| Attribute     | Detail                                                                          |
| ------------- | ------------------------------------------------------------------------------- |
| Name          | **HaulPave**                                                                    |
| Scope         | Pavement structure design + operating-cost analysis for mine haul roads         |
| License       | MIT                                                                             |
| Language      | Python 3.10+                                                                    |
| Package Name  | `haulpave`                                                                      |
| Repository    | `github.com/rahmadjenss/haulpave` (proposed)                                    |
| Documentation | MkDocs + GitHub Pages                                                           |
| PyPI          | `pip install haulpave`                                                          |

---

## 2. Scope Boundary

This section exists to prevent scope creep and to be honest about what v1.0 will and won't cover.

### In Scope (v0.1 → v1.0)

| Domain                  | What's Included                                                          |
| ----------------------- | ------------------------------------------------------------------------ |
| Traffic loading         | Fleet composition → CESA and design coverages (AASHTO-based)            |
| Pavement structure      | Layer thickness design via CBR-based method (USACE / Bina Marga)        |
| Material properties     | CBR, elastic modulus, basic classification for common mine road materials |
| Vehicle database        | Specifications for common haul trucks and support vehicles               |
| Operating cost analysis | Scenario-based cost comparison with explicit assumptions                  |
| Reporting               | Structured summaries in code, Excel export                               |

### Explicitly Out of Scope

| Domain                        | Why It's Out                                                           |
| ----------------------------- | ---------------------------------------------------------------------- |
| Geometric design              | Different discipline; requires alignment/profile software (Civil 3D)   |
| Drainage design               | Requires hydrology, not just pavement mechanics                        |
| Berm / safety bund design     | Governed by mine safety regulations, not pavement engineering          |
| Intersection / ramp design    | Geometric + traffic ops problem                                        |
| Grade / gradient optimization | Requires pit design integration                                        |
| Ride quality (IRI/roughness)  | Requires time-series monitoring data, not design-stage analysis        |
| Maintenance scheduling        | Operations domain; HaulPave estimates cost, not schedule               |
| Traffic simulation            | Different tool category (fleet management software)                    |
| FEM / advanced numerical      | Deferred to post-v1.0 if demand exists                                 |

### Scope Evolution Policy

New features are only added when:

1. They have a clear published engineering method backing them.
2. At least one benchmark case exists to test against.
3. They don't compromise the reliability of existing modules.
4. A maintainer (or contributor) commits to owning the validation.

---

## 3. Target Users & Use Cases

### Primary Users

| Persona                    | Context                                        | Key Need                             |
| -------------------------- | ---------------------------------------------- | ------------------------------------ |
| Mine Planning Engineer     | Designs haul road network for new/expanding pit | Quick, defensible thickness estimate |
| Geotechnical Engineer      | Specifies pavement structure for construction   | Traceable method with clear inputs   |
| Cost/Control Engineer      | Evaluates road investment vs operating cost     | Scenario cost comparison             |
| EPC Proposal Engineer      | Prepares tender for road improvement works      | Structured design summary            |
| Mining Engineering Student | Learning haul road design principles            | Transparent, educational codebase    |

### Core Use Cases

| ID    | Use Case                                                  | Phase |
| ----- | --------------------------------------------------------- | ----- |
| UC-01 | Define a fleet → compute design CESA and coverages        | 1     |
| UC-02 | Given coverages + subgrade CBR → determine pavement thickness | 1 |
| UC-03 | Look up vehicle specifications from built-in registry     | 1     |
| UC-04 | Run a complete design and export a structured summary     | 1     |
| UC-05 | Compare thickness results across methods (with caveats)   | 2     |
| UC-06 | Compare operating costs across 2–3 pavement scenarios     | 3     |
| UC-07 | Perform sensitivity analysis on key design variables      | 2     |
| UC-08 | Export a styled Excel design summary                      | 3     |

---

## 4. Engineering Methodology

### 4.1 The v0.1 Calculation Chain (Exact Definition)

The v0.1 pipeline uses two frameworks in a defined sequence. This section exists to make the boundary between them explicit and prevent framework-mixing ambiguity.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     v0.1 CALCULATION CHAIN                         │
│                                                                     │
│  STEP 1: TRAFFIC BOOKKEEPING (AASHTO-based)                       │
│  ┌───────────────────────────────────────────┐                     │
│  │  Fleet composition                         │                     │
│  │  ↓                                         │                     │
│  │  Per-vehicle axle loads → LEF (AASHTO)     │                     │
│  │  ↓                                         │                     │
│  │  Cumulative ESA (CESA) over design life    │                     │
│  │  ↓                                         │                     │
│  │  OUTPUT A: CESA summary (traffic report)   │                     │
│  └───────────────────────────────────────────┘                     │
│                          │                                          │
│                          │ (CESA is a reporting/summary metric.     │
│                          │  It is NOT the direct input to the       │
│                          │  structural design method below.)        │
│                          │                                          │
│  STEP 2: STRUCTURAL DESIGN (USACE CBR-derived)                    │
│  ┌───────────────────────────────────────────┐                     │
│  │  Direct inputs from fleet data:            │                     │
│  │  • Design wheel load (kN) — heaviest       │                     │
│  │    single-wheel load from fleet             │                     │
│  │  • Tire contact pressure (kPa)              │                     │
│  │  • Number of coverages/passes               │                     │
│  │    (derived from fleet trips, NOT from CESA)│                     │
│  │                                              │                     │
│  │  Direct input from site data:               │                     │
│  │  • Subgrade CBR (%)                          │                     │
│  │                                              │                     │
│  │  ↓                                           │                     │
│  │  USACE empirical thickness determination     │                     │
│  │  ↓                                           │                     │
│  │  OUTPUT B: Required total cover thickness    │                     │
│  │  OUTPUT C: Recommended layer structure       │                     │
│  └───────────────────────────────────────────┘                     │
│                                                                     │
│  The CESA from Step 1 appears in the design report as a traffic    │
│  context metric. It is NOT used as a substitute for the USACE      │
│  native traffic variables (wheel load, pressure, coverages).       │
└─────────────────────────────────────────────────────────────────────┘
```

**Why this matters:** AASHTO ESAL normalization and USACE CBR design speak different "traffic languages." ESAL reduces mixed traffic to an equivalent 80 kN standard axle; USACE works with actual wheel loads and pass counts. Conflating them — feeding an ESAL number into a USACE formula that expects coverages — would produce meaningless results. HaulPave keeps both computations intact but clearly separates their roles:

- **CESA** is for traffic reporting, fleet dominance analysis, and future compatibility with methods that do use ESA natively (e.g., TRH 14 in Phase 2).
- **Wheel load / tire pressure / coverages** are the actual structural design inputs for v0.1.

### 4.2 Canonical Method for v0.1: CBR-Based Design (USACE-Derived)

The first release implements one structural method only: the CBR-based empirical design derived from USACE (US Army Corps of Engineers) methodology, adapted for heavy mining vehicles.

**Why this method first:**

- It is the most widely understood pavement design method globally.
- Input requirements are minimal: subgrade CBR, wheel load, tire pressure, coverages.
- It is the method most commonly used (or misused) in Indonesian mining practice.
- Validation is straightforward: hand calculations are tractable.

**What the method does:**

```
INPUTS:
  - Subgrade CBR (%)
  - Design wheel load (kN) — from the heaviest vehicle in the fleet
  - Tire contact pressure (kPa) — from the design vehicle's tire spec
  - Design coverages — from fleet pass count over design life

PROCESS:
  1. Compute required total cover thickness using USACE empirical curves
     (digitized per Curve Encoding Policy, Section 4.5).
  2. Distribute total thickness across layers based on material quality:
     - Wearing course: minimum 150 mm
     - Base course: minimum 200 mm (CBR ≥ 80)
     - Sub-base: remainder
  3. Apply material substitution adjustments if non-standard materials used.

OUTPUT:
  - Recommended PavementStructure (layer types, thicknesses, material requirements)
  - Design coverages and CESA (as traffic context)
  - Full assumptions log
  - Confidence label
```

**Known limitations of this method:**

- Purely empirical — does not model actual stress/strain in layers.
- Originally calibrated for military airfield pavements, not mine roads. The adaptation to mine vehicles introduces uncertainty.
- Does not account for moisture variation, freeze-thaw, or dynamic loading effects.
- CBR itself is an index test with known reproducibility issues.
- Design curves are graphical and require digitization (see Section 4.5).

These limitations are documented in every output, not hidden.

### 4.3 Additional Methods (Phase 2)

Phase 2 introduces TRH 14 (South African method) — selected because it was specifically developed for mine haul roads and is the closest thing to a purpose-built standard.

**Critical design decision: methods are NOT directly comparable.**

Each method has its own input classification system, calibration context, and implicit assumptions about construction quality, drainage, and maintenance. HaulPave will present multi-method results side by side with explicit disclaimers, not as interchangeable answers. The comparison engine will include:

1. **Method Applicability Matrix** — which method is most appropriate for which conditions.
2. **Assumption Sheet** — what each method assumes about drainage, compaction, climate, etc.
3. **Input Mapping Warnings** — where the same raw input (e.g., CBR = 8%) maps to different categories across methods.
4. **Divergence Flags** — if results differ by more than a threshold, the tool flags this as "requires engineering review" rather than averaging or picking one.

Methods are never averaged, blended, or reconciled algorithmically. The goal is to inform engineering judgment, not to replace it with a false consensus.

### 4.4 References: Implemented vs. Referenced

| Reference                        | Status in v0.1         | Status in v1.0          |
| -------------------------------- | ---------------------- | ----------------------- |
| USACE TM 5-822-12               | **Implemented**        | Implemented             |
| AASHTO Pavement Design Guide    | **Implemented** (ESAL/LEF) | Implemented         |
| TRH 14 (South Africa)           | Referenced only        | **Implemented**         |
| ARRB Special Report 73          | Referenced only        | Evaluated for inclusion |
| Thompson & Visser (2006)         | Referenced only        | Implemented (economics) |
| Tannant & Regensburg (2001)      | Referenced only        | Referenced              |
| Kaufman & Ault (1977)            | Referenced only        | Referenced (economics)  |
| Bina Marga Pd T-01-2002-B       | Referenced only        | Adapted where applicable|
| Caterpillar Performance Handbook | **Data source**        | Data source             |
| Komatsu Spec Handbook            | **Data source**        | Data source             |

"Referenced" means the document informs understanding but is not encoded as a computable method. "Implemented" means the method is in code, tested, and producing outputs. "Data source" means factual parameters are extracted (see Section 4.6 for provenance policy).

### 4.5 Curve Encoding Policy

Several design methods in HaulPave rely on graphical empirical curves rather than closed-form equations. Because digitization introduces its own uncertainty, HaulPave applies the following policy:

**Source documentation:** Every encoded curve must cite the exact source figure (document title, edition/year, page number, figure number).

**Digitization method:** Curves are digitized by extracting control points at sufficient density to capture curvature changes. The digitization tool or method used (e.g., manual reading, WebPlotDigitizer) is recorded.

**Stored representation:** Digitized curves are stored as versioned JSON files of (x, y) control points in the `src/haulpave/design/curves/` directory. Each file includes metadata: source citation, digitization date, number of control points, and author.

**Interpolation:** Between control points, HaulPave uses monotonic cubic spline interpolation (`scipy.interpolate.PchipInterpolator`) by default. The interpolation method is recorded in the curve metadata and can be overridden if a different method better fits the curve's behavior.

**Tolerance:** Benchmark expected values are tied to a specific encoded curve version. Acceptable deviation between HaulPave's interpolated result and a hand-read value from the original chart is documented per curve (typically ±5% or ±10 mm, whichever is greater).

**Versioning:** Curve data files are versioned (e.g., `usace_cbr_v1.json`). If a curve is re-digitized with higher fidelity or from a newer edition, a new version is created. Previous versions are retained for reproducibility. Benchmark tests reference a specific curve version.

```
src/haulpave/design/curves/
├── usace_cbr_v1.json          # USACE TM 5-822-12, Fig 3-2
├── usace_cbr_v1.meta.yaml     # Source, digitization method, tolerance
├── trh14_catalogue_v1.json    # TRH 14 Table 4.2 (Phase 2)
└── trh14_catalogue_v1.meta.yaml
```

### 4.6 OEM Data Provenance Policy

HaulPave's vehicle registry contains factual engineering parameters (gross vehicle weight, axle loads, tire specifications, payload ratings) extracted from publicly available manufacturer documentation such as the Caterpillar Performance Handbook and Komatsu Specifications & Application Handbook.

**What is stored:** Factual engineering parameters with source attribution (document title, edition, page or table number).

**What is NOT stored or redistributed:** Proprietary OEM handbook content, scanned pages, reproduced tables, charts, or any copyrighted material beyond what is necessary for citation and traceability.

**Contributor requirement:** Every vehicle entry in the registry must include a `source` field citing the specific document and location of the data. Entries without source attribution are not accepted.

### 4.7 Units Policy

Unit ambiguity is one of the most avoidable failure modes in engineering software. HaulPave applies the following rule:

**Internal representation:** All values are stored and computed in SI units. The canonical units for each domain are:

| Quantity            | Internal Unit | Symbol |
| ------------------- | ------------- | ------ |
| Length / thickness  | millimeters   | mm     |
| Distance            | kilometers    | km     |
| Force / load        | kilonewtons   | kN     |
| Pressure / stress   | kilopascals   | kPa    |
| Mass                | tonnes (Mg)   | t      |
| Area                | square cm     | cm²    |
| Cost                | USD           | USD    |
| Time                | years / days  | yr / d |

**User input:** Input YAML/JSON files must use SI units as listed above. A `utils/units.py` module provides explicit conversion helpers (e.g., `psi_to_kpa()`, `tons_to_tonnes()`, `inches_to_mm()`) for users who source data in imperial units. Implicit conversion is never performed.

**Report output:** Every numerical value in a report output is accompanied by its unit. No bare numbers.

### 4.8 Report Versioning Policy

For engineering software, versioning is part of defensibility — not just convenience. Every generated design report includes the following metadata:

| Field              | Example                          | Purpose                              |
| ------------------ | -------------------------------- | ------------------------------------ |
| `haulpave_version` | `0.1.0`                         | Package version                      |
| `method_id`        | `cbr_usace_v1`                  | Design method identifier + version   |
| `curve_version`    | `usace_cbr_v1`                  | Curve data version used (if applicable) |
| `confidence`       | `benchmark_tested`              | Confidence label                     |
| `generated_at`     | `2026-04-15T14:30:00+07:00`     | Timestamp (ISO 8601 with timezone)   |
| `input_hash`       | `sha256:a1b2c3...`              | Hash of the input configuration file |

This allows any output to be traced back to the exact code, method version, curve data, and input that produced it. If a design is questioned, the audit trail is built in.

---

## 5. Technical Architecture

### 5.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────┐
│                   USER INTERFACES                    │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │   CLI    │  │ Python API   │  │ Web UI (post   │ │
│  │ haulpave │  │ import       │  │ v1.0, maybe)   │ │
│  └────┬─────┘  └──────┬───────┘  └───────┬────────┘ │
│       │                │                  │          │
├───────┴────────────────┴──────────────────┴──────────┤
│                    CORE ENGINE                       │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Traffic    │  │   Pavement   │  │  Economics  │ │
│  │   Module     │  │   Design     │  │   Module    │ │
│  │              │  │   Module     │  │             │ │
│  │  ESAL/CESA   │  │  CBR (v0.1)  │  │  Scenario   │ │
│  │  Coverages   │  │  TRH14 (v0.2)│  │  calculator │ │
│  │  Fleet comp. │  │              │  │  w/ explicit │ │
│  │              │  │              │  │  assumptions │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│         │                 │                 │        │
├─────────┴─────────────────┴─────────────────┴────────┤
│                    DATA LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Vehicle    │  │   Material   │  │   Curve    │ │
│  │   Registry   │  │   Library    │  │   Data     │ │
│  │  (YAML)      │  │   (YAML)     │  │   (JSON)   │ │
│  │  w/ source   │  │  non-normative│  │  versioned │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │          Benchmark Dossier (tests/)           │    │
│  │   Hand-calc cases, published case studies     │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

### 5.2 Repository Structure

```
haulpave/
├── pyproject.toml
├── README.md
├── LICENSE                        # MIT
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SCOPE.md                       # Living scope boundary document
├── mkdocs.yml
│
├── src/
│   └── haulpave/
│       ├── __init__.py
│       ├── py.typed
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── vehicle.py
│       │   ├── material.py
│       │   ├── pavement.py
│       │   ├── traffic.py
│       │   └── economics.py
│       │
│       ├── vehicle_registry/
│       │   ├── __init__.py
│       │   ├── registry.py
│       │   └── data/
│       │       ├── caterpillar.yaml
│       │       ├── komatsu.yaml
│       │       └── hitachi.yaml
│       │
│       ├── material_library/
│       │   ├── __init__.py
│       │   ├── library.py
│       │   └── data/
│       │       └── common_granular.yaml   # Non-normative templates
│       │
│       ├── traffic/
│       │   ├── __init__.py
│       │   ├── esal.py             # AASHTO ESAL/CESA (traffic reporting)
│       │   ├── lef.py              # Load Equivalency Factor
│       │   ├── coverages.py        # Design coverages/passes (for USACE)
│       │   └── fleet.py            # Fleet composition
│       │
│       ├── design/
│       │   ├── __init__.py
│       │   ├── base.py             # Abstract base
│       │   ├── cbr_method.py       # v0.1 canonical method
│       │   ├── trh14.py            # v0.2
│       │   ├── comparison.py       # v0.2 — with disclaimers
│       │   └── curves/             # Versioned empirical curve data
│       │       ├── usace_cbr_v1.json
│       │       ├── usace_cbr_v1.meta.yaml
│       │       └── README.md       # Curve encoding policy summary
│       │
│       ├── economics/              # v0.3
│       │   ├── __init__.py
│       │   ├── scenario.py         # Scenario-based cost comparison
│       │   ├── tire_cost.py        # Tire replacement cost model
│       │   ├── fuel_cost.py        # Rolling resistance → fuel estimate
│       │   └── summary.py          # Delta cost table, payback, sensitivity
│       │
│       ├── reporting/
│       │   ├── __init__.py
│       │   ├── metadata.py         # Report versioning (package ver, method, curve, hash)
│       │   ├── text_report.py      # Plain text / Markdown summary
│       │   └── excel_report.py     # Styled Excel export (v0.3)
│       │
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py             # Typer CLI
│       │
│       └── utils/
│           ├── __init__.py
│           ├── units.py            # Explicit unit conversion helpers
│           └── interpolation.py    # Curve interpolation (PCHIP default)
│
├── tests/
│   ├── conftest.py
│   ├── test_traffic/
│   │   ├── test_esal.py
│   │   ├── test_coverages.py
│   │   └── test_fleet.py
│   ├── test_design/
│   │   └── test_cbr_method.py
│   └── benchmarks/                  # THE BENCHMARK DOSSIER
│       ├── README.md                # Explains each benchmark case
│       ├── bench_01_cesa_hand_calc.py
│       ├── bench_02_coverages_hand_calc.py
│       ├── bench_03_cbr_usace_example.py
│       ├── bench_04_published_case.py
│       └── reference_data/
│           ├── bench_01_expected.json
│           ├── bench_02_expected.json
│           ├── bench_03_expected.json
│           ├── bench_04_expected.json
│           └── sources.md           # Full citations for all benchmark data
│
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   ├── scope.md
│   ├── concepts/
│   │   ├── traffic-loading.md       # CESA vs coverages, why both exist
│   │   └── cbr-design.md
│   ├── methodology/
│   │   ├── v01-calculation-chain.md  # The exact v0.1 pipeline
│   │   ├── cbr-method.md            # Theory, derivation, limitations
│   │   ├── curve-encoding.md        # How graphical methods are digitized
│   │   ├── trh14-method.md          # Added when implemented
│   │   └── method-comparison.md     # Why methods differ, how to interpret
│   ├── policies/
│   │   ├── units.md
│   │   ├── versioning.md
│   │   ├── oem-data-provenance.md
│   │   └── material-library-disclaimer.md
│   ├── limitations.md
│   └── references.md
│
└── examples/
    ├── 01_quick_design.py
    ├── 02_fleet_analysis.py
    └── configs/
        └── sample_project.yaml
```

### 5.3 Data Models

Key design principles in these models:

- TrafficInput supports simple whole-road mode only in v0.1. Segment-level modeling is structurally prepared but explicitly experimental/post-v0.1.
- MaterialLayer includes field-relevant properties but entries are labeled as non-normative templates.
- Economics models are scenario calculators with mandatory assumption transparency.
- Every result carries a confidence label.

```python
# ============================================================
# VEHICLE MODELS
# ============================================================

class TireSpec(BaseModel):
    """Tire specification for a mining vehicle."""
    size: str                              # e.g., "40.00R57"
    inflation_pressure_kpa: float
    contact_area_cm2: float
    cost_usd: float | None = None
    expected_life_hours: float | None = None
    source: str | None = None

class AxleGroup(BaseModel):
    """Single axle or axle group on a vehicle."""
    axle_type: Literal["single", "tandem", "tridem"]
    num_tires: int
    tire_spec: TireSpec
    load_empty_kn: float
    load_laden_kn: float
    spacing_mm: float | None = None

class MiningVehicle(BaseModel):
    """Complete specification of a mining haul truck or support vehicle."""
    id: str
    manufacturer: str
    model: str
    category: Literal[
        "haul_truck", "water_truck", "grader",
        "dozer", "loader", "light_vehicle", "other"
    ]
    gvw_empty_tonnes: float
    gvw_laden_tonnes: float
    payload_tonnes: float
    axle_groups: list[AxleGroup]
    speed_laden_kmh: float = 30.0
    speed_empty_kmh: float = 40.0
    source: str                            # REQUIRED — data provenance


# ============================================================
# TRAFFIC MODELS
# ============================================================

class FleetUnit(BaseModel):
    """A vehicle type and its operational parameters within a fleet."""
    vehicle_id: str                        # Reference to vehicle registry
    quantity: int
    trips_per_day: float                   # Round trips per unit per day
    growth_rate_pct: float = 0.0

class HaulSegment(BaseModel):
    """
    A specific segment of haul road with its own traffic characteristics.
    EXPERIMENTAL — not officially supported in v0.1.
    """
    segment_id: str
    length_km: float
    direction: Literal["two_way", "uphill_laden", "downhill_laden"]
    laden_lane: Literal["left", "right", "both"]
    fleet: list[FleetUnit]
    lane_distribution_factor: float = 1.0
    notes: str = ""

class TrafficInput(BaseModel):
    """
    Traffic loading specification for design.

    v0.1 officially supports simple whole-road mode only.
    Segment-aware traffic loading is structurally prepared but
    reserved for a later release after the simple pipeline is
    benchmark-tested.

    Two modes:
    1. Simple mode (v0.1): single fleet for whole road.
    2. Segment mode (post-v0.1, experimental): per-segment fleet
       and directionality.
    """
    # Simple mode (v0.1 — officially supported)
    fleet: list[FleetUnit] | None = None
    directional_factor: float = 0.5

    # Segment mode (experimental, post-v0.1)
    segments: list[HaulSegment] | None = None

    # Common
    design_life_years: int = 10
    operating_days_per_year: int = 350

    @model_validator(mode="after")
    def must_have_fleet_or_segments(self) -> "TrafficInput":
        if not self.fleet and not self.segments:
            raise ValueError("Provide either 'fleet' (simple) or 'segments' (detailed)")
        if self.segments:
            import warnings
            warnings.warn(
                "Segment-level traffic is experimental and not yet benchmark-tested. "
                "Use simple whole-road mode for production designs.",
                stacklevel=2,
            )
        return self

class TrafficResult(BaseModel):
    """
    Output of traffic analysis.

    Contains BOTH:
    - CESA (for traffic reporting / TRH14 compatibility)
    - Coverages (for USACE CBR structural input)
    """
    total_cesa: float
    cesa_by_vehicle: dict[str, float]
    annual_esa: float
    dominant_vehicle: str
    dominant_pct: float

    # USACE-native traffic outputs
    design_wheel_load_kn: float            # Heaviest single-wheel load
    design_tire_pressure_kpa: float        # From design vehicle
    design_coverages: float                # Pass count for design

    method: Literal["aashto"]


# ============================================================
# MATERIAL MODELS
# ============================================================

class MaterialLayer(BaseModel):
    """
    A single layer in the pavement structure.

    IMPORTANT: Built-in material library entries using these fields
    are convenience templates for early-stage analysis and education.
    They are NOT normative design values and must be replaced or
    confirmed with site-specific laboratory and field data before
    use in real projects.
    """
    name: str                              # e.g., "Wearing Course"
    material_type: str                     # e.g., "coarse_sand", "crushed_OB"
    thickness_mm: float

    # Strength / stiffness
    cbr: float | None = None               # Design CBR (soaked, 95% MDD)
    elastic_modulus_mpa: float | None = None
    poissons_ratio: float = 0.35

    # Field properties
    compaction_target: str | None = None    # e.g., "95% MDD", "98% MDD"
    plasticity_index: float | None = None   # PI
    max_particle_size_mm: float | None = None
    fines_content_pct: float | None = None  # % passing 0.075mm
    moisture_sensitivity: Literal[
        "low", "moderate", "high", "unknown"
    ] = "unknown"

    # Reinforcement
    reinforcement: Literal[
        "none", "geotextile_woven", "geotextile_nonwoven",
        "geogrid_biaxial", "geogrid_uniaxial"
    ] = "none"

    # Cost
    unit_cost_per_m3: float | None = None

    # Provenance
    source: str | None = None
    is_template: bool = False              # True if from built-in library
    notes: str = ""


class SubgradeInfo(BaseModel):
    """Subgrade characterization — separated from pavement layers."""
    cbr: float
    cbr_test_condition: Literal[
        "soaked", "unsoaked", "field", "assumed"
    ] = "soaked"
    elastic_modulus_mpa: float | None = None
    moisture_condition: Literal[
        "dry", "optimum", "wet", "saturated", "unknown"
    ] = "unknown"
    drainage_condition: Literal[
        "good", "fair", "poor", "unknown"
    ] = "unknown"
    notes: str = ""


class PavementStructure(BaseModel):
    """Complete pavement structure from top to subgrade."""
    layers: list[MaterialLayer]
    subgrade: SubgradeInfo

    @computed_field
    @property
    def total_thickness_mm(self) -> float:
        return sum(layer.thickness_mm for layer in self.layers)


# ============================================================
# DESIGN RESULT
# ============================================================

class DesignResult(BaseModel):
    """
    Output of a pavement design calculation.

    Every result carries its assumptions, limitations, confidence level,
    and version metadata so it remains auditable.
    """
    method: str
    method_reference: str                  # Full citation
    method_version: str                    # e.g., "cbr_usace_v1"
    curve_version: str | None = None       # e.g., "usace_cbr_v1" if applicable
    required_thickness_mm: float
    recommended_structure: PavementStructure
    design_coverages: float
    design_cesa: float                     # For reporting context
    subgrade_cbr: float
    assumptions: list[str]                 # REQUIRED
    limitations: list[str]                 # REQUIRED
    confidence: Literal[
        "benchmark_tested",
        "method_implemented",
        "experimental"
    ]

    # Report versioning
    haulpave_version: str
    generated_at: str                      # ISO 8601 with timezone
    input_hash: str                        # SHA-256 of input config

    notes: list[str] = []


# ============================================================
# ECONOMICS MODELS (scenario calculator, not predictor)
# ============================================================

class CostAssumptions(BaseModel):
    """
    Explicit assumptions behind an economic scenario.

    This model exists because economic analysis is only as good
    as its assumptions. Every assumption is visible, not buried.
    """
    fuel_price_usd_per_liter: float
    tire_cost_usd_per_unit: float
    grading_cost_usd_per_km: float
    grading_interval_days: int
    rolling_resistance_source: Literal[
        "thompson_visser_2006",
        "caterpillar_handbook",
        "user_provided"
    ] = "thompson_visser_2006"
    notes: str = ""


class CostScenario(BaseModel):
    """
    Economic analysis for a road design scenario.

    Answers "IF these assumptions hold, THEN these are the costs."
    Does NOT predict actual costs.
    """
    name: str
    pavement: PavementStructure
    road_length_km: float
    road_width_m: float
    assumptions: CostAssumptions           # REQUIRED
    analysis_period_years: int = 10

    # Computed by engine
    construction_cost_usd: float | None = None
    annual_maintenance_usd: float | None = None
    annual_tire_impact_usd: float | None = None
    annual_fuel_impact_usd: float | None = None


class EconomicResult(BaseModel):
    """
    Result of comparative economic analysis.

    v0.3 scope: delta cost table, payback estimate, sensitivity.
    NPV/BCR deferred to a later, more mature economics layer
    after the base scenario calculator is proven reliable.
    """
    scenarios: list[CostScenario]

    # v0.3 outputs
    delta_cost_table: dict[str, dict[str, float]]    # scenario → cost category → delta
    payback_years: dict[str, float | None]            # scenario → payback vs baseline
    sensitivity_summary: dict[str, str] | None = None # key variable → qualitative impact

    # Deferred to post-v0.3
    # npv_by_scenario: dict[str, float]
    # bcr_by_scenario: dict[str, float | None]

    caveat: str = (
        "These results are scenario-based estimates, not predictions. "
        "Actual outcomes depend on site conditions, construction quality, "
        "maintenance practices, and operator behavior. "
        "All key assumptions are listed per scenario."
    )
```

---

## 6. Development Roadmap

### Reality Check

This project is built by a solo developer working full-time as a civil engineer. That means:

- Evenings + weekends = ~10–15 productive hours/week on this project.
- The most expensive work is not coding — it's validation, sourcing vehicle data, digitizing curves, and writing honest documentation.
- Shipping a small, correct, well-documented tool is worth more than shipping a large, impressive, untested one.

### Phase 0 — Benchmark First (Week 1–4)

**Goal**: Before writing any design logic, establish the benchmark cases that will validate it.

| Week | Deliverable                                                                    |
| ---- | ------------------------------------------------------------------------------ |
| 1    | Repository setup: pyproject.toml, CI (ruff + mypy + pytest), pre-commit        |
| 1    | Pydantic data models for Vehicle, Traffic, Pavement                            |
| 2    | **Benchmark 01**: CESA hand calculation — 3 fleet compositions, full working   |
| 2    | **Benchmark 02**: Coverages hand calculation — same fleets, USACE pass counts  |
| 3    | **Benchmark 03**: CBR thickness — 3 subgrade/traffic combos, cited USACE curves |
| 3    | Digitize USACE design curves → `usace_cbr_v1.json` with metadata              |
| 4    | **Benchmark 04**: Published/reproducible case — thesis, technical note, or anonymized internal case with sufficient input transparency |
| 4    | Write `tests/benchmarks/` with all expected results as test fixtures           |

**Phase 0 Definition of Done:**

- Benchmark cases exist as documented test fixtures before any engine code.
- Each benchmark cites its source (document, page, equation/figure number).
- USACE design curves are digitized, versioned, with interpolation method documented.
- Running `pytest tests/benchmarks/` fails (engine code doesn't exist yet) — but the tests are valid.

### Phase 1 — MVP: One Method, Working (Week 5–12)

**Goal**: `pip install haulpave` works. Engineer can compute CESA, coverages, and CBR thickness. All benchmark cases pass.

| Week  | Deliverable                                                                    |
| ----- | ------------------------------------------------------------------------------ |
| 5–6   | Vehicle registry: 10–15 haul trucks (CAT, Komatsu, Hitachi) with cited sources |
| 5–6   | ESAL/CESA calculator + coverages calculator                                    |
| 7–8   | CBR-based thickness design engine using digitized curves                       |
| 8–9   | All 4 benchmark cases pass                                                     |
| 9–10  | CLI: `haulpave design --config project.yaml`                                   |
| 10    | Text-based design report with full versioning metadata                         |
| 11    | Material library: 5–8 common granular materials (labeled as non-normative)     |
| 11    | Docs: README, Getting Started, v0.1 calculation chain, CBR method, limitations |
| 12    | **Release v0.1.0 to PyPI**                                                     |

**v0.1.0 delivers exactly:**

- Fleet input → CESA + coverages → CBR-based thickness → structured output with versioned metadata.
- One design method, benchmark-tested.
- Honest documentation including limitations, scope boundary, and material library disclaimer.
- Simple whole-road traffic mode only. Segment-level is structurally present but marked experimental.

### Phase 2 — Second Method + Comparison (Week 13–24)

**Goal**: TRH 14 implemented. Multi-method comparison with proper caveats.

| Week  | Deliverable                                                                    |
| ----- | ------------------------------------------------------------------------------ |
| 13–15 | TRH 14 benchmark cases (3 cases from TRH 14 handbook)                         |
| 16–18 | TRH 14 design engine — passes benchmarks                                      |
| 19–20 | Method Applicability Matrix document                                           |
| 20–21 | Comparison engine with assumption sheets and divergence flags                  |
| 22    | Sensitivity analysis utility (vary CBR, traffic ±20%)                         |
| 23    | Expanded vehicle registry (20–25 vehicles)                                     |
| 24    | **Release v0.2.0**                                                             |

### Phase 3 — Economics as Scenario Calculator (Week 25–36)

**Goal**: Scenario-based cost comparison. All assumptions visible. No false precision.

| Week  | Deliverable                                                                    |
| ----- | ------------------------------------------------------------------------------ |
| 25–27 | CAPEX estimation (material quantity × unit cost)                               |
| 28–30 | Rolling resistance → fuel cost model (Thompson & Visser basis, with caveats)   |
| 30–32 | Tire replacement cost model (surface type categories, not predictive)          |
| 33–34 | Delta cost table + payback estimate + sensitivity table                        |
| 35    | Excel report export (styled, with mandatory assumption sheet tab)             |
| 36    | **Release v0.3.0**                                                             |

**Economics v0.3 scope:** delta costs, payback, sensitivity. NPV/BCR deferred to a later release after the base scenario calculator has been used in practice and its assumption framework proven reliable.

### Phase 4 — Documentation, Cases & Community (Week 37–44)

**Goal**: Tool is well-documented enough for others to use, trust, and contribute to.

| Week  | Deliverable                                                                    |
| ----- | ------------------------------------------------------------------------------ |
| 37–39 | Complete methodology docs (CBR derivation, TRH 14 walkthrough, curve encoding) |
| 40–41 | 1–2 case studies from real projects (anonymized if needed)                     |
| 42–43 | Contributing guide with "good first issues"                                    |
| 43–44 | Technical blog post / LinkedIn article for launch                              |
| 44    | **Release v1.0.0**                                                             |

### Total Timeline: ~44 weeks (~11 months)

---

## 7. Decisions Log

Hard decisions that shape what HaulPave is and isn't.

| #  | Decision                                              | Rationale                                                                  |
| -- | ----------------------------------------------------- | -------------------------------------------------------------------------- |
| 1  | CBR method is canonical for v0.1                      | Most widely understood, tractable to validate, serves 80% of use cases     |
| 2  | TRH 14 is the second method, not ARRB or ME           | Purpose-built for mine roads; ARRB and ME deferred to post-v1.0            |
| 3  | Methods are never averaged or blended                  | Different calibration contexts make blending misleading                    |
| 4  | CESA and coverages are both computed but serve different roles | CESA for traffic reporting; coverages for USACE structural input    |
| 5  | Economics is a scenario calculator, not a predictor    | Input uncertainty too high for "prediction" language                       |
| 6  | NPV/BCR deferred from v0.3                             | Delta cost + payback provides decision support without false precision     |
| 7  | Benchmark dossier before code                          | Prevents shipping untested calculations                                   |
| 8  | Vehicle data requires source citation                  | Reproducibility; prevents garbage-in                                      |
| 9  | Material library entries are non-normative templates   | Site materials vary dramatically; built-in values are starting points only |
| 10 | No web UI before v1.0                                  | Focus on getting the engine right before building a frontend               |
| 11 | MIT license                                            | Maximum adoption potential                                                 |
| 12 | Python-first, no custom compiled extensions            | Lower barrier for engineers who aren't software developers. NumPy/SciPy are standard scientific Python dependencies, not custom compiled code |
| 13 | v0.1 supports simple whole-road mode only              | Segment-level modeling increases validation burden; deferred until simple pipeline is proven |
| 14 | SI units internally, explicit conversion only          | Eliminates unit ambiguity — a common engineering software failure mode     |
| 15 | Every report output carries version metadata           | Engineering defensibility requires full audit trail                        |
| 16 | Empirical curves are versioned, digitization documented | Reproducibility of graphical method implementations                       |

---

## 8. Quality Assurance

### 8.1 Benchmark Dossier (First-Class Deliverable)

The benchmark dossier is built before the engine. It contains:

1. **Benchmark 01 — CESA hand calculation**: 3 fleet compositions, step-by-step AASHTO LEF and CESA computation, expected results with full working.
2. **Benchmark 02 — Coverages hand calculation**: Same 3 fleets, USACE-native pass count computation, expected results.
3. **Benchmark 03 — CBR thickness**: 3 subgrade/traffic combinations, hand-computed from USACE curves with cited figure/page numbers. Expected results tied to a specific curve version (`usace_cbr_v1`). Tolerance: ±5% or ±10 mm, whichever is greater.
4. **Benchmark 04 — Published/reproducible case**: At least one publicly reproducible case study, worked example, thesis, technical note, or anonymized internal case with sufficient input transparency to reproduce the result.

Each benchmark includes: exact input data, exact expected output, source citation (document, page, equation/figure), acceptable tolerance with justification, and the curve version used (if applicable).

### 8.2 Testing Strategy

```
┌────────────────────────────┐
│   Benchmark Tests          │  ← Does our code match published results?
│   ~20% of tests            │    (Most important. Built first.)
├────────────────────────────┤
│   Module Integration       │  ← Does fleet → CESA → thickness pipeline work?
│   ~30% of tests            │
├────────────────────────────┤
│   Unit Tests               │  ← Individual functions, edge cases, input validation
│   ~50% of tests            │
└────────────────────────────┘
```

### 8.3 CI Pipeline

```yaml
on: [push, pull_request]

jobs:
  lint:   ruff check + ruff format --check
  types:  mypy --strict
  test:   pytest --cov=haulpave (threshold: ≥ 85%)
  bench:  pytest tests/benchmarks/ -v (must all pass — this is non-negotiable)
  docs:   mkdocs build --strict
```

### 8.4 Confidence Labeling

Every `DesignResult` carries a `confidence` field:

| Level                | Meaning                                                     |
| -------------------- | ----------------------------------------------------------- |
| `benchmark_tested`   | Output matches published hand-calc or case study            |
| `method_implemented` | Code follows the method faithfully, not yet benchmarked     |
| `experimental`       | Adaptation or extension — use with extra caution            |

Users see this in every output. No result is presented without its confidence level.

---

## 9. Risk Register

| Risk                                  | Likelihood   | Impact       | Mitigation                                                                   |
| ------------------------------------- | ------------ | ------------ | ---------------------------------------------------------------------------- |
| Inaccurate design output              | Medium       | **Critical** | Benchmark dossier first; confidence labeling; limitations documented         |
| Scope creep beyond pavement design    | High         | High         | SCOPE.md as living document; explicit out-of-scope list                      |
| Multi-method comparison misleads users| Medium       | High         | Applicability matrix; assumption sheets; divergence flags                    |
| Curve digitization introduces error   | Medium       | Medium       | Curve encoding policy; tolerance spec; version pinning in benchmarks         |
| Vehicle data accuracy                 | Medium       | Medium       | Source citation required; community review; no proprietary redistribution    |
| Material library treated as normative | Medium       | High         | `is_template` flag; disclaimer in docs and model docstring                   |
| Economics treated as prediction       | Medium       | High         | "Scenario calculator" language; mandatory CostAssumptions; NPV/BCR deferred |
| Solo maintainer burnout               | **High**     | High         | Realistic timeline; MVP-first; seek co-maintainer after v0.2                 |
| Low adoption                          | Medium       | Medium       | Quality > features; case studies; LinkedIn outreach                          |
| Unit ambiguity in I/O                 | Low          | Medium       | SI-internal policy; explicit conversion utilities; units on every output     |

---

## 10. Dependencies

### Runtime

| Package    | Purpose                      | Version | Notes                     |
| ---------- | ---------------------------- | ------- | ------------------------- |
| pydantic   | Data validation & models     | ≥ 2.0   | Core                      |
| numpy      | Numerical computation        | ≥ 1.24  | Core                      |
| scipy      | Interpolation (PCHIP curves) | ≥ 1.11  | Core                      |
| pyyaml     | Config / data file loading   | ≥ 6.0   | Core                      |
| typer      | CLI framework                | ≥ 0.9   | Core                      |
| rich       | Terminal formatting           | ≥ 13.0  | Core                      |

### Optional (extras)

| Package    | Purpose                | Install with              | Phase |
| ---------- | ---------------------- | ------------------------- | ----- |
| matplotlib | Cross-section diagrams | `pip install haulpave[viz]`| 2+    |
| openpyxl   | Excel report export    | `pip install haulpave[excel]` | 3  |

### Development

| Package         | Purpose        |
| --------------- | -------------- |
| pytest          | Testing        |
| pytest-cov      | Coverage       |
| ruff            | Lint + format  |
| mypy            | Type checking  |
| mkdocs-material | Documentation  |
| pre-commit      | Git hooks      |

---

## 11. Success Metrics (Conservative)

| Metric                  | 6-Month    | 12-Month   |
| ----------------------- | ---------- | ---------- |
| Benchmark cases passing | ≥ 4        | ≥ 8        |
| PyPI monthly downloads  | 50         | 200        |
| GitHub stars            | 20         | 80         |
| Contributors            | 1 (me)     | 3–5        |
| Implemented methods     | 1 (CBR)    | 2 (+ TRH14)|
| Vehicles in registry    | 15         | 25+        |
| Published case studies  | 0          | 1–2        |

These are deliberately conservative. Hitting them means the project is healthy.

---

## 12. License & Disclaimer

**License**: MIT — maximum openness.

**Disclaimer** (included in README, every report output, and material library):

> HaulPave is an engineering analysis tool provided "as is" without warranty of any kind. Pavement designs generated by this software must be reviewed, verified, and approved by a qualified professional engineer with knowledge of site-specific conditions before being used for construction. The authors accept no liability for designs based on this software's output.

**Material Library Disclaimer** (included in library docs and MaterialLayer docstring):

> Built-in material entries are convenience templates for early-stage analysis and education. They are NOT normative design values and must be replaced or confirmed with site-specific laboratory and field data before use in real projects.

**OEM Data Statement:**

> Vehicle registry entries store factual engineering parameters with source attribution. The project does not redistribute proprietary OEM handbook content, scans, or reproduced tables beyond what is necessary for citation and traceability.

---

## 13. Day 1 Actions

```bash
# 1. Create repository
mkdir haulpave && cd haulpave
git init
gh repo create rahmadjenss/haulpave --public \
  --description "Open-source pavement structure and operating-cost analysis toolkit for mine haul roads"

# 2. Initialize Python project
uv init --lib --name haulpave

# 3. Create structure
mkdir -p src/haulpave/{models,vehicle_registry/data,material_library/data,traffic,design/curves,economics,reporting,cli,utils}
mkdir -p tests/{test_traffic,test_design,benchmarks/reference_data}
mkdir -p docs/{concepts,methodology,policies}
mkdir -p examples/configs

# 4. Create scope boundary document
touch SCOPE.md

# 5. First commit
git add .
git commit -m "chore: initial project structure"
git push -u origin main

# 6. FIRST REAL TASK:
#    Open tests/benchmarks/ and start writing benchmark cases.
#    Not the engine. The benchmarks.
#    Then digitize USACE design curves.
```

---

*HaulPave — Design better haul roads. Move more dirt. Waste less.*
*Built with honesty about what it can and can't do.*
