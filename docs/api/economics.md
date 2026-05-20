# Economics Module

Module: `src/haulpave/economics/`

Scenario-based operating cost analysis for mine haul roads — single-scenario
calculation and cross-surface rolling-resistance cost comparison.

---

## `compute_economics(scenario: CostScenario, trips_per_day: float = 0.0, working_days_per_year: int = 250) -> EconomicsResult`

Compute operating cost for a haul road scenario using unit-cost summation
per trip (fuel + tyre + maintenance + operator).

**Source:** `src/haulpave/economics/engine.py:76`

| Parameter | Type | Description |
|-----------|------|-------------|
| `scenario` | `CostScenario` | Haul geometry, fleet parameters, and cost assumptions |
| `trips_per_day` | `float` | One-way trips per day (0 to skip annual calculation) |
| `working_days_per_year` | `int` | Operating days per year (default 250) |

**Returns:** `EconomicsResult`

---

## `EconomicsResult`

```python
@dataclass(frozen=True)
class EconomicsResult:
    scenario_id: str
    cost_per_trip: float
    cost_per_tonne_km: float
    fuel_cost_per_trip: float
    tyre_cost_per_trip: float
    maintenance_cost_per_trip: float
    operator_cost_per_trip: float
    trips_per_year: float
    annual_cost: float
    currency: str
    method: str = "haulpave-economics-v1"
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"]
```

**Source:** `src/haulpave/economics/engine.py:29`

| Attribute | Description |
|-----------|-------------|
| `scenario_id` | Identifier from the input scenario |
| `cost_per_trip` | Total cost per one-way trip [currency] |
| `cost_per_tonne_km` | Unit transport cost [currency / (t·km)] |
| `fuel_cost_per_trip` | Fuel component of cost per trip [currency] |
| `tyre_cost_per_trip` | Tyre wear component of cost per trip [currency] |
| `maintenance_cost_per_trip` | Maintenance component of cost per trip [currency] |
| `operator_cost_per_trip` | Operator component of cost per trip [currency] |
| `trips_per_year` | Annual trip count (0 if not provided) |
| `annual_cost` | Annual operating cost (0 if not provided) |
| `currency` | ISO 4217 currency code |
| `method` | Human-readable method identifier |
| `confidence` | Confidence label per project plan §4.3 |

---

## `to_economic_result(result: EconomicsResult) -> EconomicResult`

Convert a detailed `EconomicsResult` dataclass to the Pydantic `EconomicResult` model.

**Source:** `src/haulpave/economics/engine.py:132`

---

## `compare_scenarios(scenarios: list[RoadScenario], fuel_price_usd_per_litre: float = 0.80, working_days_per_year: int = 250) -> ComparisonResult`

Compare annual operating costs across road surface scenarios using a
rolling-resistance linear cost model.

**Source:** `src/haulpave/economics/compare.py:81`

| Parameter | Type | Description |
|-----------|------|-------------|
| `scenarios` | `list[RoadScenario]` | Scenarios to compare (order preserved in output) |
| `fuel_price_usd_per_litre` | `float` | Fuel price [USD/L] (default 0.80) |
| `working_days_per_year` | `int` | Operating days per year (default 250) |

**Returns:** `ComparisonResult`

---

## `RoadScenario`

```python
class RoadScenario(BaseModel):
    name: str
    surface: Literal["asphalt", "gravel", "concrete"]
    thickness_mm: float  # Pavement design thickness [mm]
    haul_distance_km: float  # One-way haul distance [km]
    trips_per_day: float  # One-way vehicle trips per day
```

**Source:** `src/haulpave/economics/compare.py:47`

---

## `ScenarioComparison`

```python
class ScenarioComparison(BaseModel):
    name: str
    tire_cost_usd_per_year: float
    fuel_cost_usd_per_year: float
    maintenance_cost_usd_per_year: float
    confidence: ConfidenceLabel = "experimental"
```

**Source:** `src/haulpave/economics/compare.py:59`

---

## `ComparisonResult`

```python
class ComparisonResult(BaseModel):
    scenarios: list[ScenarioComparison]
    method: str = "haulpave-economics-rr-v1"
    confidence: ConfidenceLabel = "experimental"
```

**Source:** `src/haulpave/economics/compare.py:71`
