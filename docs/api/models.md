# Models Module

Module: `src/haulpave/models/`

Pydantic data models for HaulPave. All models use SI units internally
(mm, km, kN, kPa, tonnes) with explicit conversion at system boundaries.

---

## Vehicle Models

### `TireSpec`

**Source:** `src/haulpave/models/vehicle.py:11`

```python
class TireSpec(BaseModel, frozen=True):
    contact_pressure_kpa: float  # Tyre contact pressure [kPa]
    contact_area_mm2: float       # Tyre contact area [mm²]
```

### `AxleGroup`

**Source:** `src/haulpave/models/vehicle.py:20`

```python
class AxleGroup(BaseModel, frozen=True):
    axle_count: int       # Number of axles in group (1–4)
    tyres_per_axle: int   # Tyres per axle (≥ 2)
    gross_load_kn: float  # Total load on axle group [kN]
    tire_spec: TireSpec
```

### `MiningVehicle`

**Source:** `src/haulpave/models/vehicle.py:31`

```python
class MiningVehicle(BaseModel, frozen=True):
    name: str                    # Vehicle make/model identifier
    gross_vehicle_mass_t: float  # Gross vehicle mass [tonnes]
    axle_groups: list[AxleGroup] # At least one axle group
    source: str                  # Mandatory provenance — OEM spec sheet reference
```

---

## Traffic Models

### `FleetUnit`

**Source:** `src/haulpave/models/traffic.py:15`

```python
class FleetUnit(BaseModel, frozen=True):
    vehicle: MiningVehicle
    trips_per_day: float  # One-way trips per day
```

### `HaulSegment`

**Source:** `src/haulpave/models/traffic.py:24`

```python
class HaulSegment(BaseModel, frozen=True):
    segment_id: str
    length_km: float       # Segment length [km]
    fleet: list[FleetUnit]
```

**Note:** This model is **experimental** — not yet benchmark-tested.

### `TrafficInput`

**Source:** `src/haulpave/models/traffic.py:49`

```python
class TrafficInput(BaseModel, frozen=True):
    fleet: list[FleetUnit]      # Fleet mix for this section
    design_life_years: float    # Pavement design life [years]
    working_days_per_year: int  # Operating days per year (default 250)
```

### `TrafficResult`

**Source:** `src/haulpave/models/traffic.py:67`

```python
class TrafficResult(BaseModel, frozen=True):
    total_coverages: float   # Equivalent design coverages
    total_esal: float        # Equivalent single-axle loads (AASHTO)
    design_life_years: float
    method: str              # Calculation method ID
```

---

## Material Models

### `MaterialLayer`

**Source:** `src/haulpave/models/material.py:15`

```python
class MaterialLayer(BaseModel, frozen=True):
    name: str                     # Material name / identifier
    cbr_percent: float | None     # California Bearing Ratio [%]
    elastic_modulus_kpa: float | None  # Elastic (resilient) modulus [kPa]
    thickness_mm: float | None    # Layer thickness [mm]
    is_template: bool             # True = indicative reference values only
    source: str | None            # Provenance reference (required when is_template=True)
```

---

## Pavement Models

### `SubgradeInfo`

**Source:** `src/haulpave/models/pavement.py:15`

```python
class SubgradeInfo(BaseModel, frozen=True):
    cbr_percent: float         # In-situ subgrade CBR [%]
    description: str | None    # Soil description or USCS class
    source: str | None         # Test report or reference
```

### `PavementStructure`

**Source:** `src/haulpave/models/pavement.py:25`

```python
class PavementStructure(BaseModel, frozen=True):
    layers: list[MaterialLayer]  # Ordered layers, surface first

    @computed_field
    @property
    def total_thickness_mm(self) -> float  # Sum of all specified layer thicknesses
```

### `DesignResult`

**Source:** `src/haulpave/models/pavement.py:42`

```python
class DesignResult(BaseModel, frozen=True):
    pavement_structure: PavementStructure
    subgrade: SubgradeInfo
    design_coverages: float
    confidence: Literal["high", "medium", "low"]
    method_id: str          # e.g. "USACE-TM5-822-12"
    package_version: str    # haul pave package version
    curve_version: str | None
    input_hash: str | None  # SHA-256 hex digest of serialised inputs
```

---

## Economics Models

### `CostAssumptions`

**Source:** `src/haulpave/models/economics.py:12`

```python
class CostAssumptions(BaseModel, frozen=True):
    fuel_cost_per_litre: float     # Fuel price [currency/L]
    tyre_cost_per_hour: float      # Tyre wear cost [currency/hr]
    maintenance_cost_per_km: float # Maintenance cost [currency/km]
    operator_cost_per_hour: float  # Operator cost [currency/hr]
    currency: str                  # ISO 4217 currency code (default "USD")
```

### `CostScenario`

**Source:** `src/haulpave/models/economics.py:30`

```python
class CostScenario(BaseModel, frozen=True):
    scenario_id: str
    haul_distance_km: float              # One-way haul distance [km]
    average_speed_kmh: float             # Average laden speed [km/h]
    payload_t: float                     # Payload per trip [tonnes]
    fuel_consumption_l_per_km: float     # Fuel consumption [L/km]
    assumptions: CostAssumptions
```

### `EconomicResult`

**Source:** `src/haulpave/models/economics.py:43`

```python
class EconomicResult(BaseModel, frozen=True):
    scenario_id: str
    cost_per_tonne_km: float  # Unit transport cost [currency/t·km]
    cost_per_trip: float      # Total cost per one-way trip [currency]
    trips_per_year: float     # Annual trip count
    annual_cost: float        # Annual operating cost [currency]
    currency: str             # ISO 4217 currency code
    method: str               # Calculation method ID
```
