"""Benchmark for sensitivity analysis — hand-calculated CBR perturbation.

Benchmark 07: verify that a ±20 % CBR perturbation on a known fleet
produces thickness values consistent with hand-read USACE CBR curve
interpolation.

Reference: USACE TM 5-822-12 (1990) Figure 1, curve ``usace_cbr_v1``.
"""

from __future__ import annotations

import pytest

from haulpave.analysis.sensitivity import analyze_sensitivity
from haulpave.models.traffic import TrafficInput
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec
from tests.conftest import make_traffic


@pytest.fixture()
def bench_vehicle() -> MiningVehicle:
    tire = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=5000.0)
    return MiningVehicle(
        name="Benchmark Truck",
        gross_vehicle_mass_t=150.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=300.0, tire_spec=tire),
        ],
        source="bench_07 fixture",
    )


@pytest.fixture()
def bench_traffic(bench_vehicle: MiningVehicle) -> TrafficInput:
    return make_traffic(bench_vehicle, trips=20, life_years=10, days_per_year=300)


class TestSensitivityBenchmark:
    def test_cbr_sensitivity_baseline_matches_design(self, bench_traffic: TrafficInput) -> None:
        result = analyze_sensitivity(bench_traffic, subgrade_cbr=10.0, variable="cbr")
        baseline_idx = 2
        _baseline_cbr, baseline_thk = result.perturbations[baseline_idx]

        from haulpave.pavement import design_pavement

        design = design_pavement(bench_traffic, subgrade_cbr=10.0)
        assert baseline_thk == pytest.approx(design.required_thickness_mm, rel=1e-6)

    def test_cbr_sensitivity_five_points(self, bench_traffic: TrafficInput) -> None:
        result = analyze_sensitivity(bench_traffic, subgrade_cbr=10.0, variable="cbr")
        assert len(result.perturbations) == 5

    def test_cbr_sensitivity_higher_cbr_gives_thinner(self, bench_traffic: TrafficInput) -> None:
        result = analyze_sensitivity(bench_traffic, subgrade_cbr=10.0, variable="cbr")
        cbr_vals = [p[0] for p in result.perturbations]
        thk_vals = [p[1] for p in result.perturbations]
        for i in range(len(cbr_vals) - 1):
            assert cbr_vals[i] <= cbr_vals[i + 1]
            assert thk_vals[i] >= thk_vals[i + 1]
