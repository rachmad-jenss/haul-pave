"""Benchmark 05 — TRH 14 hand-calc: CBR-to-material-class mapping and thickness design.

Source:
  CSRA (1985). Technical Recommendations for Highways 14 (TRH 14):
  Guidelines for Road Construction Materials. Committee of State Road
  Authorities, Pretoria.

References:
  Thompson, R.J. and Visser, A.T. (2006). "The Functional Design of Surface
  Mine Haul Roads." Journal of the South African Institute of Mining and
  Metallurgy, vol. 106, pp. 29-36.

Method overview
---------------
TRH 14 classifies subgrade support using the G1–G9 material-class system
(TRH 14, Table 2), where higher G numbers indicate weaker material:

  G1: CBR ≥ 80   G2: CBR ≥ 45   G3: CBR ≥ 25   G4: CBR ≥ 15
  G5: CBR ≥ 7    G6: CBR ≥ 4    G7: CBR ≥ 2    G8: CBR ≥ 1.5  G9: CBR < 1.5

Design traffic uses the USACE TM 5-822-12 design-coverages method (bench_02).
Total pavement thickness is read from the TRH 14 design catalog (Thompson &
Visser 2006, Table 3) using log-linear interpolation between coverage knots.

Benchmark fleet: "Fleet D — Generic 100t Haul Truck"
------------------------------------------------------
  Single vehicle type:
    Front axle: 130 kN — single (n=1), 2 tyres → wheel_load = 65.0 kN
    Rear tandem: 520 kN — tandem (n=2), 4 tyres/axle (dual) → wheel_load = 32.5 kN
    Trips/day: 25
  Design parameters:
    Design life:   3 years
    Working days:  300 days/year

Hand-calc: design coverages
----------------------------
  Design wheel load = max(65.0, 32.5) = 65.0 kN  (governed by front axle)

  Front: positions = 1,  ratio = (65.0/65.0)^4 = 1.0
    Contrib = 25 × 2 × 1 × 1.0000 = 50.0 equiv_passes/day

  Rear tandem (dual-tyre stations):
    positions = 2 × 4 = 8,  ratio = (32.5/65.0)^4 = 0.5^4 = 0.0625
    Contrib = 25 × 2 × 8 × 0.0625 = 25.0 equiv_passes/day

  Total equiv_passes/day = 50.0 + 25.0 = 75.0
  Total coverages = 75.0 × 300 × 3 = 67,500

Hand-calc: thickness design at 67,500 coverages
-------------------------------------------------
  G6 (CBR 5%): log-linear between 10,000→425 mm and 100,000→575 mm
    frac = log10(6.75) / log10(10) = 0.8293
    T = 425 + 0.8293 × 150 = 549.4 mm  (tolerance ±25 mm)

  G5 (CBR 12%): log-linear between 10,000→325 mm and 100,000→450 mm
    T = 325 + 0.8293 × 125 = 428.7 mm  (tolerance ±25 mm)

  G4 (CBR 20%): log-linear between 10,000→225 mm and 100,000→300 mm
    T = 225 + 0.8293 × 75  = 287.2 mm  (tolerance ±25 mm)

Catalog provenance
------------------
  Source:  Thompson & Visser (2006) Table 3 — structural design catalogue
           for mine haul roads (based on TRH 14 / CSRA 1985), adapted for
           unpaved roads. Values rounded to nearest 25 mm (graphical accuracy).
  Catalog: trh14_catalog_v1 (to be encoded in DAS-112).
"""

from __future__ import annotations

import json
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Guard: skip entire module if TRH 14 engine not yet implemented.
# pytest.importorskip causes a module-level skip (not a failure) when the
# target module is absent.  CI stays green until DAS-112 is complete.
# ---------------------------------------------------------------------------
trh14_mod = pytest.importorskip(
    "haulpave.pavement.trh14",
    reason="TRH 14 pavement design engine not yet implemented — tracked in DAS-112",
)
cbr_to_material_class = trh14_mod.cbr_to_material_class
compute_trh14 = trh14_mod.compute_trh14

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
_REF = json.loads(
    (pathlib.Path(__file__).parent / "reference_data" / "bench_05_expected.json").read_text(
        encoding="utf-8"
    )
)

_TOL = _REF["metadata"]["tolerances"]
THICKNESS_TOLERANCE_MM = _TOL["thickness_mm"]  # 25.0 mm
COVERAGES_TOLERANCE = _TOL["coverages_pct"] / 100.0  # 0.001 → 0.1 %

_FLEET_REF = _REF["fleet"]["vehicles"][0]
DESIGN_LIFE = _REF["fleet"]["design_life_years"]  # 3
WORKING_DAYS = _REF["fleet"]["working_days_per_year"]  # 300

# ---------------------------------------------------------------------------
# Fleet D fixture — single 100t haul truck
# ---------------------------------------------------------------------------
from haulpave.models.traffic import FleetUnit, TrafficInput  # noqa: E402
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec  # noqa: E402

_PLACEHOLDER_TIRE = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=50000.0)


def _single(load_kn: float) -> AxleGroup:
    """Single axle group: 1 axle, 2 tyres."""
    return AxleGroup(
        axle_count=1,
        tyres_per_axle=2,
        gross_load_kn=load_kn,
        tire_spec=_PLACEHOLDER_TIRE,
    )


def _tandem(load_kn: float) -> AxleGroup:
    """Tandem axle group: 2 axles, 4 tyres per axle (dual-tyre stations)."""
    return AxleGroup(
        axle_count=2,
        tyres_per_axle=4,
        gross_load_kn=load_kn,
        tire_spec=_PLACEHOLDER_TIRE,
    )


@pytest.fixture()
def fleet_d_input() -> TrafficInput:
    """Fleet D — Generic 100t haul truck, single vehicle type.

    Front single axle : 130 kN   → wheel_load = 65.0 kN  (design wheel)
    Rear tandem group : 520 kN   → wheel_load = 32.5 kN  (dual-tyre)
    Trips per day     : 25
    Design life       : 3 years
    Working days      : 300 days/year

    Expected coverages: 67,500  (hand-calc in module docstring)
    """
    truck = MiningVehicle(
        name=_FLEET_REF["name"],
        gross_vehicle_mass_t=_FLEET_REF["gross_vehicle_mass_t"],
        axle_groups=[
            _single(_FLEET_REF["front_axle_load_kN"]),
            _tandem(_FLEET_REF["rear_tandem_load_kN"]),
        ],
        source="Generic 100t haul truck — bench_05 design fixture",
    )
    return TrafficInput(
        fleet=[FleetUnit(vehicle=truck, trips_per_day=_FLEET_REF["trips_per_day"])],
        design_life_years=DESIGN_LIFE,
        working_days_per_year=WORKING_DAYS,
    )


# ---------------------------------------------------------------------------
# Tests: CBR → G-class mapping
# ---------------------------------------------------------------------------
_G_CLASS_CASES = _REF["cbr_to_material_class_cases"]


@pytest.mark.parametrize(
    "cbr,expected_class,note",
    [(c["cbr"], c["expected"], c["note"]) for c in _G_CLASS_CASES],
    ids=[c["note"].split(" → ")[0].strip() for c in _G_CLASS_CASES],
)
def test_cbr_to_material_class(cbr: float, expected_class: str, note: str) -> None:
    """CBR → G-class mapping must match TRH 14 Table 2 boundaries.

    Boundaries are inclusive on the lower bound: CBR=7 → G5 (not G6).
    """
    result = cbr_to_material_class(cbr)
    assert result == expected_class, (
        f"CBR={cbr}% should map to {expected_class}, got '{result}'. Note: {note}"
    )


# ---------------------------------------------------------------------------
# Tests: end-to-end thickness design (Fleet D at 67,500 coverages)
# ---------------------------------------------------------------------------
_THICKNESS_CASES = {c["id"]: c for c in _REF["thickness_cases"]}


def _assert_thickness(computed: float, expected: float, label: str) -> None:
    """Assert computed thickness is within THICKNESS_TOLERANCE_MM of reference."""
    err = abs(computed - expected)
    assert err <= THICKNESS_TOLERANCE_MM, (
        f"{label}: computed={computed:.2f} mm, expected={expected:.2f} mm, "
        f"absolute error={err:.2f} mm (tolerance={THICKNESS_TOLERANCE_MM:.1f} mm)"
    )


def _assert_coverages(computed: float, expected: float, label: str) -> None:
    """Assert computed coverages is within COVERAGES_TOLERANCE of reference."""
    rel_err = abs(computed - expected) / expected
    assert rel_err <= COVERAGES_TOLERANCE, (
        f"{label}: computed={computed:.2f}, expected={expected:.2f}, "
        f"relative error={rel_err:.4%} (tolerance={COVERAGES_TOLERANCE:.2%})"
    )


def test_bench05_case_a_g6_thickness(fleet_d_input: TrafficInput) -> None:
    """Fleet D, CBR=5% (G6): total thickness must match TRH 14 design catalog.

    Hand-calc:
      G6, 67,500 coverages → log-linear between 10,000→425 mm and 100,000→575 mm
      frac = log10(6.75) / 1.0 = 0.8293
      T = 425 + 0.8293 × 150 = 549.4 mm  (tolerance ±25 mm)
    """
    case = _THICKNESS_CASES["case_a_g6"]
    result = compute_trh14(fleet_d_input, subgrade_cbr=case["subgrade_cbr"])

    assert result.material_class == case["expected_g_class"], (
        f"Expected G-class '{case['expected_g_class']}', got '{result.material_class}'"
    )
    _assert_coverages(result.total_coverages, case["expected_coverages"], "Case A coverages")
    _assert_thickness(
        result.total_thickness_mm, case["expected_total_thickness_mm"], "Case A (G6) thickness"
    )


def test_bench05_case_b_g5_thickness(fleet_d_input: TrafficInput) -> None:
    """Fleet D, CBR=12% (G5): total thickness must match TRH 14 design catalog.

    Hand-calc:
      G5, 67,500 coverages → log-linear between 10,000→325 mm and 100,000→450 mm
      frac = 0.8293
      T = 325 + 0.8293 × 125 = 428.7 mm  (tolerance ±25 mm)
    """
    case = _THICKNESS_CASES["case_b_g5"]
    result = compute_trh14(fleet_d_input, subgrade_cbr=case["subgrade_cbr"])

    assert result.material_class == case["expected_g_class"], (
        f"Expected G-class '{case['expected_g_class']}', got '{result.material_class}'"
    )
    _assert_coverages(result.total_coverages, case["expected_coverages"], "Case B coverages")
    _assert_thickness(
        result.total_thickness_mm, case["expected_total_thickness_mm"], "Case B (G5) thickness"
    )


def test_bench05_case_c_g4_thickness(fleet_d_input: TrafficInput) -> None:
    """Fleet D, CBR=20% (G4): total thickness must match TRH 14 design catalog.

    Hand-calc:
      G4, 67,500 coverages → log-linear between 10,000→225 mm and 100,000→300 mm
      frac = 0.8293
      T = 225 + 0.8293 × 75 = 287.2 mm  (tolerance ±25 mm)
    """
    case = _THICKNESS_CASES["case_c_g4"]
    result = compute_trh14(fleet_d_input, subgrade_cbr=case["subgrade_cbr"])

    assert result.material_class == case["expected_g_class"], (
        f"Expected G-class '{case['expected_g_class']}', got '{result.material_class}'"
    )
    _assert_coverages(result.total_coverages, case["expected_coverages"], "Case C coverages")
    _assert_thickness(
        result.total_thickness_mm, case["expected_total_thickness_mm"], "Case C (G4) thickness"
    )


# ---------------------------------------------------------------------------
# Monotonicity checks — physical constraints
# ---------------------------------------------------------------------------
class TestTRH14Monotonicity:
    """Verify physical constraints on TRH 14 design outcomes.

    These tests do not require specific numeric values; they enforce the
    engineering invariants that must hold for any valid implementation:

    1. Stronger subgrade (higher CBR) → less thickness required.
    2. G-class ordinal: G1 (strongest) < G2 < ... < G9 (weakest).
    3. All thickness values are strictly positive.
    """

    def test_thickness_decreases_with_cbr(self, fleet_d_input: TrafficInput) -> None:
        """Higher CBR subgrade must require less total pavement thickness."""
        result_weak = compute_trh14(fleet_d_input, subgrade_cbr=5.0)  # G6
        result_medium = compute_trh14(fleet_d_input, subgrade_cbr=12.0)  # G5
        result_strong = compute_trh14(fleet_d_input, subgrade_cbr=20.0)  # G4

        assert result_weak.total_thickness_mm > result_medium.total_thickness_mm, (
            f"CBR=5% (G6) should require more thickness than CBR=12% (G5): "
            f"{result_weak.total_thickness_mm:.1f} vs {result_medium.total_thickness_mm:.1f} mm"
        )
        assert result_medium.total_thickness_mm > result_strong.total_thickness_mm, (
            f"CBR=12% (G5) should require more thickness than CBR=20% (G4): "
            f"{result_medium.total_thickness_mm:.1f} vs {result_strong.total_thickness_mm:.1f} mm"
        )

    def test_thickness_positive(self, fleet_d_input: TrafficInput) -> None:
        """Required thickness must always be strictly positive."""
        for cbr in [5.0, 12.0, 20.0, 35.0]:
            result = compute_trh14(fleet_d_input, subgrade_cbr=cbr)
            assert result.total_thickness_mm > 0, (
                f"Thickness must be positive for CBR={cbr}%, got {result.total_thickness_mm:.2f} mm"
            )

    def test_g_class_ordering(self) -> None:
        """Material class must follow the TRH 14 G-class ordering.

        G1 (strongest) → G9 (weakest): higher CBR must give lower G number.
        """
        cbr_g_pairs = [
            (95.0, "G1"),
            (60.0, "G2"),
            (35.0, "G3"),
            (20.0, "G4"),
            (10.0, "G5"),
            (5.0, "G6"),
            (3.0, "G7"),
            (1.8, "G8"),
            (0.8, "G9"),
        ]
        for cbr, expected in cbr_g_pairs:
            assert cbr_to_material_class(cbr) == expected, (
                f"CBR={cbr}% should give {expected}, got '{cbr_to_material_class(cbr)}'"
            )
