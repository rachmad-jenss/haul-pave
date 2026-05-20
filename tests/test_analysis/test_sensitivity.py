"""Unit tests for haulpave.analysis.sensitivity."""

from __future__ import annotations

import pytest

from haulpave.analysis.sensitivity import SensitivityResult, analyze_sensitivity
from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.models.vehicle import AxleGroup, MiningVehicle, TireSpec


def _make_traffic(trips: float = 10.0, life: float = 5.0) -> TrafficInput:
    tire = TireSpec(contact_pressure_kpa=700.0, contact_area_mm2=5000.0)
    vehicle = MiningVehicle(
        name="Test Truck",
        gross_vehicle_mass_t=100.0,
        axle_groups=[
            AxleGroup(axle_count=1, tyres_per_axle=2, gross_load_kn=200.0, tire_spec=tire),
        ],
        source="test fixture",
    )
    fleet_unit = FleetUnit(vehicle=vehicle, trips_per_day=trips)
    return TrafficInput(fleet=[fleet_unit], design_life_years=life, working_days_per_year=300)


class TestAnalyzeSensitivity:
    def test_cbr_sensitivity_returns_correct_structure(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(traffic, subgrade_cbr=10.0, variable="cbr")
        assert isinstance(result, SensitivityResult)
        assert result.variable == "cbr"
        assert result.baseline == 10.0
        assert len(result.perturbations) == 5

    def test_cbr_sensitivity_perturbations_ordered(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(traffic, subgrade_cbr=10.0, variable="cbr")
        cbr_vals = [p[0] for p in result.perturbations]
        thickness_vals = [p[1] for p in result.perturbations]
        assert cbr_vals == sorted(cbr_vals)
        assert thickness_vals == sorted(thickness_vals, reverse=True)

    def test_cbr_sensitivity_midpoint_matches_baseline(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(traffic, subgrade_cbr=10.0, variable="cbr")
        mid_cbr, mid_thk = result.perturbations[2]
        assert mid_cbr == pytest.approx(10.0)

    def test_cbr_sensitivity_clamps_at_boundary(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(traffic, subgrade_cbr=2.0, variable="cbr", range_pct=50.0)
        cbr_vals = [p[0] for p in result.perturbations]
        assert cbr_vals[0] >= 1.0

    def test_cbr_sensitivity_lower_cbr_gives_thicker_pavement(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(traffic, subgrade_cbr=15.0, variable="cbr")
        cbr_vals = [p[0] for p in result.perturbations]
        thk_vals = [p[1] for p in result.perturbations]
        for i in range(len(cbr_vals) - 1):
            if cbr_vals[i] < cbr_vals[i + 1]:
                assert thk_vals[i] >= thk_vals[i + 1]

    def test_coverages_sensitivity_returns_correct_structure(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(traffic, subgrade_cbr=10.0, variable="coverages")
        assert result.variable == "coverages"
        assert result.baseline > 0
        assert len(result.perturbations) == 5

    def test_coverages_sensitivity_monotonic(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(traffic, subgrade_cbr=10.0, variable="coverages")
        cov_vals = [p[0] for p in result.perturbations]
        thk_vals = [p[1] for p in result.perturbations]
        for i in range(len(cov_vals) - 1):
            assert cov_vals[i] <= cov_vals[i + 1]
            assert thk_vals[i] <= thk_vals[i + 1]

    def test_design_life_sensitivity(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(traffic, subgrade_cbr=10.0, variable="design_life")
        assert result.variable == "design_life"
        assert result.baseline == 5.0
        assert len(result.perturbations) == 5

    def test_design_life_longer_gives_thicker(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(traffic, subgrade_cbr=10.0, variable="design_life")
        life_vals = [p[0] for p in result.perturbations]
        thk_vals = [p[1] for p in result.perturbations]
        for i in range(len(life_vals) - 1):
            if life_vals[i] < life_vals[i + 1]:
                assert thk_vals[i] <= thk_vals[i + 1]

    def test_sensitivity_with_curved_id(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(
            traffic, subgrade_cbr=10.0, variable="cbr", curve_id="usace_cbr_v1"
        )
        assert result.variable == "cbr"

    def test_invalid_variable_raises(self) -> None:
        traffic = _make_traffic()
        with pytest.raises(ValueError, match="Unknown variable"):
            analyze_sensitivity(traffic, subgrade_cbr=10.0, variable="invalid")  # type: ignore[arg-type]

    def test_negative_range_pct_raises(self) -> None:
        traffic = _make_traffic()
        with pytest.raises(ValueError, match="range_pct"):
            analyze_sensitivity(traffic, subgrade_cbr=10.0, variable="cbr", range_pct=-10.0)

    def test_non_traffic_input_raises(self) -> None:
        with pytest.raises(TypeError, match="TrafficInput"):
            analyze_sensitivity("not traffic", subgrade_cbr=10.0, variable="cbr")  # type: ignore[arg-type]

    def test_confidence_label(self) -> None:
        traffic = _make_traffic()
        result = analyze_sensitivity(traffic, subgrade_cbr=10.0, variable="cbr")
        assert result.confidence == "medium"
