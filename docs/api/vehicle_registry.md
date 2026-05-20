# Vehicle Registry Module

Module: `src/haulpave/vehicle_registry/`

Canonical specifications for mining haul trucks — a catalogue of `VehicleEntry`
records suitable for UI selection lists and seeding bridge scenarios.

---

## `list_all() -> list[VehicleEntry]`

Return all registered vehicle entries.

**Source:** `src/haulpave/vehicle_registry/__init__.py:104`

---

## `find_by_id(vehicle_id: str) -> VehicleEntry | None`

Return the registry entry for `vehicle_id`, or `None` if not found.

**Source:** `src/haulpave/vehicle_registry/__init__.py:109`

---

## `VehicleEntry`

```python
class VehicleEntry(BaseModel, frozen=True):
    id: str            # Unique vehicle identifier slug
    name: str          # Vehicle display name
    gvw_kn: float      # Gross vehicle weight at rated payload [kN]
    axles: int         # Number of axle groups
    vehicle: MiningVehicle  # Full specification for engine use
```

**Source:** `src/haulpave/vehicle_registry/__init__.py:21`

---

## Registered Vehicles

| ID | Name | GVW [kN] | Axle Groups |
|----|------|----------|-------------|
| `cat-797f` | Caterpillar 797F | 6,104 | 2 (front single, rear tandem) |
| `cat-789d` | Caterpillar 789D | 3,304 | 2 (front single, rear tandem) |
| `kom-960e` | Komatsu 960E | 5,925 | 2 (front single, rear tandem) |
| `cat-785d` | Caterpillar 785D | 2,641 | 2 (front single, rear tandem) |

All entries use a 25% front / 75% rear gross-weight split (CAT Performance
Handbook Edition 47) and standard OTR tyre spec (700 kPa, 50,000 mm²).
