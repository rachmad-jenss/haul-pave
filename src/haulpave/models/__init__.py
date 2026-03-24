"""Pydantic data models for HaulPave — public API.

All models use SI units internally:
- Distances: mm (layer thickness) or km (haul distance)
- Forces / loads: kN
- Pressures / stiffness: kPa
- Masses: tonnes
- No implicit unit mixing — convert explicitly at system boundaries.
"""

from haulpave.models.economics import CostAssumptions, CostScenario, EconomicResult
from haulpave.models.material import MaterialLayer
from haulpave.models.pavement import DesignResult, PavementStructure, SubgradeInfo
from haulpave.models.traffic import FleetUnit, HaulSegment, TrafficInput, TrafficResult
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec

__all__ = [
    # vehicle
    "TireSpec",
    "AxleGroup",
    "MiningVehicle",
    # traffic
    "FleetUnit",
    "HaulSegment",
    "TrafficInput",
    "TrafficResult",
    # material
    "MaterialLayer",
    # pavement
    "SubgradeInfo",
    "PavementStructure",
    "DesignResult",
    # economics
    "CostAssumptions",
    "CostScenario",
    "EconomicResult",
]
