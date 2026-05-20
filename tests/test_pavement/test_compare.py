"""Unit tests for haulpave.pavement.compare.

Tests cover:
  - compare_methods: return type, field values, delta arithmetic
  - ComparisonResult: both sub-results are correct types
  - Fleet D × 3 CBR values (G4/G5/G6) — same fleet as bench_05
  - Error propagation from sub-engines
  - Default curve_id behaviour
"""

from __future__ import annotations

import pytest

from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.models.vehicle import MiningVehicle
from haulpave.pavement import PavementResult, compare_methods
from haulpave.pavement.compare import ComparisonResult
from haulpave.pavement.trh14 import TRH14Result

from ..conftest import make_single_axle, make_tandem_axle


@pytest.fixture()
def fleet_d() -> TrafficInput:
    """Fleet D — bench_05 fixture: Generic 100t haul truck, 25 trips/day.

    design_wheel_load = 65.0 kN (front axle governs)
    total_coverages   = 75.0 × 300 × 3 = 67,500
    """
    truck = MiningVehicle(
        name="Generic 100t Haul Truck",
        gross_vehicle_mass_t=100.0,
        axle_groups=[make_single_axle(130.0), make_tandem_axle(520.0)],
        source="bench_05 design fixture",
    )
    return TrafficInput(
        fleet=[FleetUnit(vehicle=truck, trips_per_day=25)],
        design_life_years=3,
        working_days_per_year=300,
    )


# ---------------------------------------------------------------------------
# Return type and structure
# ---------------------------------------------------------------------------
class TestCompareMethodsReturnType:
    def test_returns_comparison_result(self, fleet_d: TrafficInput) -> None:
        result = compare_methods(fleet_d, subgrade_cbr=12.0)
        assert isinstance(result, ComparisonResult)

    def test_usace_field_is_pavement_result(self, fleet_d: TrafficInput) -> None:
        result = compare_methods(fleet_d, subgrade_cbr=12.0)
        assert isinstance(result.usace, PavementResult)

    def test_trh14_field_is_trh14_result(self, fleet_d: TrafficInput) -> None:
        result = compare_methods(fleet_d, subgrade_cbr=12.0)
        assert isinstance(result.trh14, TRH14Result)

    def test_fields_present(self, fleet_d: TrafficInput) -> None:
        result = compare_methods(fleet_d, subgrade_cbr=12.0)
        assert result.subgrade_cbr == pytest.approx(12.0)
        assert result.curve_id == "usace_cbr_v1"
        assert "USACE" in result.method
        assert "TRH 14" in result.method
        assert result.confidence == "benchmark_tested"


# ---------------------------------------------------------------------------
# Delta arithmetic — core invariant
# ---------------------------------------------------------------------------
class TestDeltaArithmetic:
    @pytest.mark.parametrize("cbr", [5.0, 12.0, 20.0])
    def test_delta_equals_trh14_minus_usace(self, fleet_d: TrafficInput, cbr: float) -> None:
        """delta_mm must exactly equal trh14 thickness − usace thickness."""
        result = compare_methods(fleet_d, subgrade_cbr=cbr)
        expected_delta = result.trh14.total_thickness_mm - result.usace.required_thickness_mm
        assert result.delta_mm == pytest.approx(expected_delta, abs=1e-9)

    def test_both_thicknesses_positive_g6(self, fleet_d: TrafficInput) -> None:
        """Both sub-engines must produce positive thickness for G6 (CBR=5%)."""
        result = compare_methods(fleet_d, subgrade_cbr=5.0)
        assert result.usace.required_thickness_mm > 0
        assert result.trh14.total_thickness_mm > 0

    def test_delta_is_float(self, fleet_d: TrafficInput) -> None:
        result = compare_methods(fleet_d, subgrade_cbr=12.0)
        assert isinstance(result.delta_mm, float)


# ---------------------------------------------------------------------------
# Sub-engine consistency — coverages and wheel load must match
# ---------------------------------------------------------------------------
class TestSubEngineConsistency:
    def test_coverages_match(self, fleet_d: TrafficInput) -> None:
        """Both sub-engines use the same coverages engine — values must agree."""
        result = compare_methods(fleet_d, subgrade_cbr=12.0)
        assert result.usace.total_coverages == pytest.approx(result.trh14.total_coverages, rel=1e-6)

    def test_design_wheel_load_match(self, fleet_d: TrafficInput) -> None:
        """Both sub-engines must use the same design wheel load."""
        result = compare_methods(fleet_d, subgrade_cbr=12.0)
        assert result.usace.design_wheel_load_kn == pytest.approx(
            result.trh14.design_wheel_load_kn, rel=1e-6
        )

    def test_g_class_matches_subgrade_cbr(self, fleet_d: TrafficInput) -> None:
        """TRH 14 G-class must be consistent with the input CBR."""
        result = compare_methods(fleet_d, subgrade_cbr=12.0)
        assert result.trh14.material_class == "G5"

        result_g6 = compare_methods(fleet_d, subgrade_cbr=5.0)
        assert result_g6.trh14.material_class == "G6"

        result_g4 = compare_methods(fleet_d, subgrade_cbr=20.0)
        assert result_g4.trh14.material_class == "G4"


# ---------------------------------------------------------------------------
# Fleet D × 3 CBR values — thickness sanity checks
# ---------------------------------------------------------------------------
class TestFleetDThicknesses:
    """Both methods should produce physically plausible results for Fleet D.

    Acceptance range (loose): 100–900 mm for mine haul road design.
    """

    _MIN_MM = 100.0
    _MAX_MM = 900.0

    @pytest.mark.parametrize("cbr", [5.0, 12.0, 20.0])
    def test_usace_thickness_in_range(self, fleet_d: TrafficInput, cbr: float) -> None:
        result = compare_methods(fleet_d, subgrade_cbr=cbr)
        assert self._MIN_MM <= result.usace.required_thickness_mm <= self._MAX_MM

    @pytest.mark.parametrize("cbr", [5.0, 12.0, 20.0])
    def test_trh14_thickness_in_range(self, fleet_d: TrafficInput, cbr: float) -> None:
        result = compare_methods(fleet_d, subgrade_cbr=cbr)
        assert self._MIN_MM <= result.trh14.total_thickness_mm <= self._MAX_MM

    def test_thickness_decreases_with_cbr_usace(self, fleet_d: TrafficInput) -> None:
        """Stronger subgrade → thinner USACE design."""
        t_g6 = compare_methods(fleet_d, subgrade_cbr=5.0).usace.required_thickness_mm
        t_g5 = compare_methods(fleet_d, subgrade_cbr=12.0).usace.required_thickness_mm
        t_g4 = compare_methods(fleet_d, subgrade_cbr=20.0).usace.required_thickness_mm
        assert t_g6 > t_g5 > t_g4

    def test_thickness_decreases_with_cbr_trh14(self, fleet_d: TrafficInput) -> None:
        """Stronger subgrade → thinner TRH 14 design."""
        t_g6 = compare_methods(fleet_d, subgrade_cbr=5.0).trh14.total_thickness_mm
        t_g5 = compare_methods(fleet_d, subgrade_cbr=12.0).trh14.total_thickness_mm
        t_g4 = compare_methods(fleet_d, subgrade_cbr=20.0).trh14.total_thickness_mm
        assert t_g6 > t_g5 > t_g4


# ---------------------------------------------------------------------------
# Default curve_id
# ---------------------------------------------------------------------------
class TestDefaultCurveId:
    def test_default_curve_id_is_usace_cbr_v1(self, fleet_d: TrafficInput) -> None:
        result = compare_methods(fleet_d, subgrade_cbr=12.0)
        assert result.curve_id == "usace_cbr_v1"

    def test_explicit_curve_id_stored(self, fleet_d: TrafficInput) -> None:
        result = compare_methods(fleet_d, subgrade_cbr=12.0, curve_id="usace_cbr_v1")
        assert result.curve_id == "usace_cbr_v1"


# ---------------------------------------------------------------------------
# Error propagation
# ---------------------------------------------------------------------------
class TestErrorPropagation:
    def test_g8_subgrade_raises(self, fleet_d: TrafficInput) -> None:
        """G8/G9 CBR (1.7%) raises ValueError — USACE curve minimum is 2.0%,
        so USACE raises before TRH 14 gets a chance to raise its own error."""
        with pytest.raises(ValueError, match="CBR"):
            compare_methods(fleet_d, subgrade_cbr=1.7)

    def test_g9_subgrade_raises(self, fleet_d: TrafficInput) -> None:
        """Very low CBR (0.5%) raises ValueError from USACE (below curve range)."""
        with pytest.raises(ValueError, match="CBR"):
            compare_methods(fleet_d, subgrade_cbr=0.5)

    def test_negative_cbr_raises(self, fleet_d: TrafficInput) -> None:
        with pytest.raises(ValueError, match="CBR"):
            compare_methods(fleet_d, subgrade_cbr=-1.0)
