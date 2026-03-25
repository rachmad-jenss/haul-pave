"""Benchmark 04 — End-to-end integration case study (Fleet B, CBR=7, 10-year design life).

End-to-end integration benchmark — USACE TM 5-822-12 worked example approach.
Exercises complete pipeline: fleet composition → CESA (AASHTO) → design coverages
(USACE) → required CBR thickness (USACE TM 5-822-12 Fig. 1).

This benchmark ties together the three prior benchmarks (Bench 01, 02, 03) into a
single end-to-end pipeline test. It mirrors the "worked example" structure of
USACE EM 1110-3-141 Appendix B and represents a typical mine access road design
following USACE TM 5-822-12 methodology.

Case definition
---------------
Fleet: "Fleet B — Medium" (identical to Bench 01 / Bench 02 Fleet B)
  - CAT 785D:    40 trips/day, front 225 kN, rear tandem 1040 kN, GVM 269 t
  - Motor Grader: 5 trips/day, front 85 kN, rear tandem 160 kN, GVM 25 t

Design parameters:
  - Subgrade CBR: 7 %
  - Design life: 10 years
  - Operating days per year: 350

Pipeline steps and expected outputs
------------------------------------
1. CESA — AASHTO 4th power law:
     Total CESA = 508,634,682.58  (from bench_01 hand-calc, ±1 %)

2. Design coverages — USACE TM 5-822-12 / EM 1110-3-141:
     Total coverages = 530,357.24  (from bench_02 hand-calc, ±2 %)

3. Required thickness — USACE TM 5-822-12 Figure 1 CBR curve (usace_cbr_v1):
     Fleet B coverages (530,357) exceed the curve's maximum tabulated level
     (100,000 coverages). Per the interpolate_thickness() specification, out-of-
     range coverage values are silently clamped to the curve boundary.
     Interpolated at CBR=7, coverages clamped to 100,000:
     Required thickness = 564.49 mm  (tolerance: ±5 mm)

Citations
---------
- USACE TM 5-822-12 (1990). "Flexible Pavement Design for Airfields." Figure 1:
  CBR design curves (digitized as usace_cbr_v1.json, provenance in meta.yaml).
- AASHTO (1993). "Guide for Design of Pavement Structures," 4th edition. 4th
  power load equivalency factor (LEF) formulation.
- USACE EM 1110-3-141 (1987). "Pavement Design for Roads, Streets, and Open
  Storage Areas, Flexible Design." Appendix B worked example structure.
- Thompson, R.J. & Visser, A.T. (2006). "The Functional Design of Surface Mine
  Haul Roads." Journal of the South African Institute of Mining and Metallurgy,
  vol. 106, pp. 29–36. (Background reference for mine haul road fleet types.)
"""

from __future__ import annotations

import json
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Import the (not yet implemented) pavement engine.
# pytest.importorskip causes the entire module to be skipped — not failed —
# when haulpave.pavement does not exist.  CI stays green until the engine is
# implemented.
# ---------------------------------------------------------------------------
pavement_mod = pytest.importorskip(
    "haulpave.pavement",
    reason="Pavement engine not yet implemented",
)
design_pavement = pavement_mod.design_pavement

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
_REF = json.loads(
    (pathlib.Path(__file__).parent / "reference_data" / "bench_04_expected.json").read_text(
        encoding="utf-8"
    )
)

_TOL = _REF["metadata"]["tolerances"]
CESA_TOLERANCE = _TOL["cesa_pct"] / 100.0  # 1 %  → 0.01
COVERAGES_TOLERANCE = _TOL["coverages_pct"] / 100.0  # 2 %  → 0.02
THICKNESS_TOLERANCE_MM = _TOL["thickness_mm"]  # 5 mm absolute

CASE = _REF["case"]
DESIGN_LIFE = CASE["design_life_years"]  # 10
WORKING_DAYS = CASE["operating_days_per_year"]  # 350
SUBGRADE_CBR = CASE["subgrade_cbr"]  # 7

# ---------------------------------------------------------------------------
# Fleet B fixtures — identical to bench_01 / bench_02 Fleet B
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
def fleet_b_input() -> TrafficInput:
    """Fleet B — Medium: CAT 785D + Motor Grader.

    Axle loads
    ----------
    CAT 785D (GVM 269 t, 40 trips/day):
      Front single axle: 225 kN  → 112.5 kN/wheel (2 tyres)
      Rear tandem group: 1040 kN → 65.0 kN/wheel (16 tyres)

    Motor Grader (GVM 25 t, 5 trips/day):
      Front single axle: 85 kN   → 42.5 kN/wheel
      Rear tandem group: 160 kN  → 10.0 kN/wheel (standard tandem, LEF=2.0)

    This composition is identical to bench_01 and bench_02 Fleet B fixtures.
    Source: Caterpillar 785D Specifications, CAT Performance Handbook Ed. 47;
            Generic motor grader — conservative GVM estimate.
    """
    cat_785d = MiningVehicle(
        name="CAT 785D",
        gross_vehicle_mass_t=269.0,
        axle_groups=[
            _single(225.0),  # front single axle: 225 kN
            _tandem(1040.0),  # rear tandem group: 1040 kN
        ],
        source="Caterpillar 785D Specifications, CAT Performance Handbook Ed. 47",
    )
    motor_grader = MiningVehicle(
        name="Motor Grader (25 t)",
        gross_vehicle_mass_t=25.0,
        axle_groups=[
            _single(85.0),  # front single axle: 85 kN
            _tandem(160.0),  # rear tandem group: 160 kN (= standard tandem → LEF 2.0)
        ],
        source="Generic motor grader — conservative estimate based on GVM",
    )
    return TrafficInput(
        fleet=[
            FleetUnit(vehicle=cat_785d, trips_per_day=40),
            FleetUnit(vehicle=motor_grader, trips_per_day=5),
        ],
        design_life_years=DESIGN_LIFE,
        working_days_per_year=WORKING_DAYS,
    )


# ---------------------------------------------------------------------------
# Test — end-to-end pipeline
# ---------------------------------------------------------------------------
def test_bench04_pipeline_fleet_b(fleet_b_input: TrafficInput) -> None:
    """End-to-end pipeline: Fleet B → CESA → coverages → CBR thickness.

    Validates all three pipeline stages against pre-computed hand-calc values
    for Fleet B (medium fleet) at CBR=7, 10-year design life.

    Stage 1 — CESA (AASHTO 4th power law):
        Expected: 508,634,682.58 ± 1 %

    Stage 2 — Design coverages (USACE TM 5-822-12):
        Expected: 530,357.24 ± 2 %

    Stage 3 — Required thickness (USACE TM 5-822-12 Fig. 1, usace_cbr_v1 curve):
        CBR=7, coverages clamped to 100,000 (curve max).
        Expected: 564.49 mm ± 5 mm

    References:
        USACE TM 5-822-12 (1990) Figure 1 CBR curves.
        AASHTO (1993) 4th power LEF.
        USACE EM 1110-3-141 (1987) Appendix B worked example structure.
    """
    result = design_pavement(
        traffic=fleet_b_input,
        subgrade_cbr=SUBGRADE_CBR,
        curve_id="usace_cbr_v1",
    )

    # --- Stage 1: CESA ---
    expected_cesa = CASE["expected_cesa"]
    cesa_rel_error = abs(result.total_cesa - expected_cesa) / expected_cesa
    assert cesa_rel_error <= CESA_TOLERANCE, (
        f"CESA stage: computed={result.total_cesa:.2f}, "
        f"expected={expected_cesa:.2f}, "
        f"relative error={cesa_rel_error:.4%} (tolerance={CESA_TOLERANCE:.1%})"
    )

    # --- Stage 2: Design coverages ---
    expected_coverages = CASE["expected_coverages"]
    cov_rel_error = abs(result.total_coverages - expected_coverages) / expected_coverages
    assert cov_rel_error <= COVERAGES_TOLERANCE, (
        f"Coverages stage: computed={result.total_coverages:.2f}, "
        f"expected={expected_coverages:.2f}, "
        f"relative error={cov_rel_error:.4%} (tolerance={COVERAGES_TOLERANCE:.1%})"
    )

    # --- Stage 3: Required thickness ---
    expected_thickness = CASE["expected_thickness_mm"]
    thickness_error = abs(result.required_thickness_mm - expected_thickness)
    assert thickness_error <= THICKNESS_TOLERANCE_MM, (
        f"Thickness stage: computed={result.required_thickness_mm:.2f} mm, "
        f"expected={expected_thickness:.2f} mm, "
        f"absolute error={thickness_error:.2f} mm (tolerance={THICKNESS_TOLERANCE_MM} mm)"
    )
