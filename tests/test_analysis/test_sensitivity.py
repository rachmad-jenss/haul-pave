"""Unit tests for haulpave.analysis.sensitivity."""

from __future__ import annotations

import pytest

from haulpave.analysis.sensitivity import SensitivityResult, analyze_sensitivity
from haulpave.models.traffic import TrafficInput
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec

from tests.conftest import make_traffic


@pytest.fixture()
def test_vehicle() -> MiningVehicle:
    tire = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=5000.0)
    return MiningVehicle(
        name="Test Truck",
        gross_vehicle_mass_t=100.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=200.0, tire_spec=tire),
        ],
        source="test fixture",
    )


@pytest.fixture()
def test_traffic(test_vehicle: MiningVehicle) -> TrafficInput:
    return make_traffic(test_vehicle, trips=10, life_years=5, days_per_year=300)


class TestAnalyzeSensitivity:
    def test_cbr_sensitivity_returns_correct_structure(self, test_traffic: TrafficInput) -> None:
        result = analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="cbr")
        assert isinstance(result, SensitivityResult)
        assert result.variable == "cbr"
        assert result.baseline == 10.0
        assert len(result.perturbations) == 5

    def test_cbr_sensitivity_perturbations_ordered(
        self, test_traffic: TrafficInput
    ) -> None:
        result = analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="cbr")
        cbr_vals = [p[0] for p in result.perturbations]
        thickness_vals = [p[1] for p in result.perturbations]
        assert cbr_vals == sorted(cbr_vals)
        assert thickness_vals == sorted(thickness_vals, reverse=True)

    def test_cbr_sensitivity_midpoint_matches_baseline(
        self, test_traffic: TrafficInput
    ) -> None:
        result = analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="cbr")
        mid_cbr, _mid_thk = result.perturbations[2]
        assert mid_cbr == pytest.approx(10.0)

    def test_cbr_sensitivity_clamps_at_boundary(
        self, test_vehicle: MiningVehicle
    ) -> None:
        traffic = make_traffic(test_vehicle, trips=10, life_years=10, days_per_year=350)
        result = analyze_sensitivity(
            traffic, subgrade_cbr=3.0, variable="cbr", range_pct=90.0
        )
        cbr_vals = [p[0] for p in result.perturbations]
        from haulpave.utils.interpolation import load_curve_data

        cbr_min = float(load_curve_data("usace_cbr_v1")["cbr_values"][0])
        assert cbr_vals[0] == pytest.approx(cbr_min)
        assert cbr_vals[-1] > cbr_vals[0]

    def test_cbr_sensitivity_lower_cbr_gives_thicker_pavement(
        self, test_traffic: TrafficInput
    ) -> None:
        result = analyze_sensitivity(test_traffic, subgrade_cbr=15.0, variable="cbr")
        cbr_vals = [p[0] for p in result.perturbations]
        thk_vals = [p[1] for p in result.perturbations]
        for i in range(len(cbr_vals) - 1):
            if cbr_vals[i] < cbr_vals[i + 1]:
                assert thk_vals[i] >= thk_vals[i + 1]

    def test_coverages_sensitivity_returns_correct_structure(
        self, test_traffic: TrafficInput
    ) -> None:
        result = analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="coverages")
        assert result.variable == "coverages"
        assert result.baseline > 0
        assert len(result.perturbations) == 5

    def test_coverages_sensitivity_monotonic(self, test_traffic: TrafficInput) -> None:
        result = analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="coverages")
        cov_vals = [p[0] for p in result.perturbations]
        thk_vals = [p[1] for p in result.perturbations]
        for i in range(len(cov_vals) - 1):
            assert cov_vals[i] <= cov_vals[i + 1]
            assert thk_vals[i] <= thk_vals[i + 1]

    def test_design_life_sensitivity(self, test_traffic: TrafficInput) -> None:
        result = analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="design_life")
        assert result.variable == "design_life"
        assert result.baseline == 5.0
        assert len(result.perturbations) == 5

    def test_design_life_longer_gives_thicker(self, test_traffic: TrafficInput) -> None:
        result = analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="design_life")
        life_vals = [p[0] for p in result.perturbations]
        thk_vals = [p[1] for p in result.perturbations]
        for i in range(len(life_vals) - 1):
            if life_vals[i] < life_vals[i + 1]:
                assert thk_vals[i] <= thk_vals[i + 1]

    def test_sensitivity_with_curve_id(self, test_traffic: TrafficInput) -> None:
        result = analyze_sensitivity(
            test_traffic, subgrade_cbr=10.0, variable="cbr", curve_id="usace_cbr_v1"
        )
        assert result.variable == "cbr"
        assert len(result.perturbations) == 5

    def test_invalid_variable_raises(self, test_traffic: TrafficInput) -> None:
        with pytest.raises(ValueError, match="Unknown variable"):
            analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="invalid")  # type: ignore[arg-type]

    def test_negative_range_pct_raises(self, test_traffic: TrafficInput) -> None:
        with pytest.raises(ValueError, match="range_pct"):
            analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="cbr", range_pct=-10.0)

    def test_zero_range_pct_raises(self, test_traffic: TrafficInput) -> None:
        with pytest.raises(ValueError, match="range_pct"):
            analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="cbr", range_pct=0.0)

    def test_confidence_label(self, test_traffic: TrafficInput) -> None:
        result = analyze_sensitivity(test_traffic, subgrade_cbr=10.0, variable="cbr")
        assert result.confidence == "medium"
