"""Unit tests for haulpave.pavement.trh14.

Tests cover:
  - cbr_to_material_class: G-class boundaries and mid-points
  - compute_trh14: return type, field values, edge cases
  - _interpolate_catalog: clamping behaviour (via compute_trh14 indirectly)
  - Error handling: negative CBR, G8/G9 subgrades
"""

from __future__ import annotations

import pytest

from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.models.vehicle import MiningVehicle
from haulpave.pavement.trh14 import (
    TRH14Result,
    cbr_to_material_class,
    compute_trh14,
    interpolate_catalog,
)

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
# cbr_to_material_class
# ---------------------------------------------------------------------------
class TestCbrToMaterialClass:
    """Verify G-class boundaries are inclusive on the lower bound."""

    @pytest.mark.parametrize(
        "cbr,expected",
        [
            (95.0, "G1"),
            (80.0, "G1"),  # lower boundary G1
            (79.9, "G2"),
            (45.0, "G2"),  # lower boundary G2
            (44.9, "G3"),
            (25.0, "G3"),  # lower boundary G3
            (24.9, "G4"),
            (15.0, "G4"),  # lower boundary G4
            (14.9, "G5"),
            (7.0, "G5"),  # lower boundary G5
            (6.9, "G6"),
            (4.0, "G6"),  # lower boundary G6
            (3.9, "G7"),
            (2.0, "G7"),  # lower boundary G7
            (1.9, "G8"),
            (1.5, "G8"),  # lower boundary G8
            (1.4, "G9"),
            (0.0, "G9"),
        ],
    )
    def test_boundary(self, cbr: float, expected: str) -> None:
        assert cbr_to_material_class(cbr) == expected, (
            f"CBR={cbr}% expected {expected}, got {cbr_to_material_class(cbr)}"
        )

    def test_negative_cbr_raises(self) -> None:
        with pytest.raises(ValueError, match="CBR must be >= 0"):
            cbr_to_material_class(-1.0)


# ---------------------------------------------------------------------------
# compute_trh14 — return type and field values
# ---------------------------------------------------------------------------
class TestComputeTrh14ReturnType:
    def test_returns_trh14result(self, fleet_d: TrafficInput) -> None:
        result = compute_trh14(fleet_d, subgrade_cbr=12.0)
        assert isinstance(result, TRH14Result)

    def test_fields_present(self, fleet_d: TrafficInput) -> None:
        result = compute_trh14(fleet_d, subgrade_cbr=12.0)
        assert result.material_class == "G5"
        assert result.total_coverages > 0
        assert result.total_thickness_mm > 0
        assert result.design_wheel_load_kn > 0
        assert "TRH 14" in result.method
        assert result.confidence == "high"

    def test_coverages_match_fleet_d(self, fleet_d: TrafficInput) -> None:
        """Fleet D produces 67,500 coverages (hand-calc, bench_05)."""
        result = compute_trh14(fleet_d, subgrade_cbr=10.0)
        assert abs(result.total_coverages - 67500.0) / 67500.0 < 0.001

    def test_design_wheel_load(self, fleet_d: TrafficInput) -> None:
        """Fleet D design wheel load = 65.0 kN (front axle governs)."""
        result = compute_trh14(fleet_d, subgrade_cbr=10.0)
        assert abs(result.design_wheel_load_kn - 65.0) < 0.01


# ---------------------------------------------------------------------------
# compute_trh14 — G-class field
# ---------------------------------------------------------------------------
class TestComputeTrh14GClass:
    @pytest.mark.parametrize(
        "cbr,expected_class",
        [(5.0, "G6"), (12.0, "G5"), (20.0, "G4"), (35.0, "G3")],
    )
    def test_g_class_correct(self, fleet_d: TrafficInput, cbr: float, expected_class: str) -> None:
        result = compute_trh14(fleet_d, subgrade_cbr=cbr)
        assert result.material_class == expected_class


# ---------------------------------------------------------------------------
# compute_trh14 — thickness values (tolerances from bench_05: ±25 mm)
# ---------------------------------------------------------------------------
class TestComputeTrh14Thickness:
    _TOL = 25.0  # mm — graphical chart reading accuracy

    def test_case_a_g6(self, fleet_d: TrafficInput) -> None:
        """CBR=5% (G6), 67,500 coverages → 549.4 mm ±25 mm."""
        result = compute_trh14(fleet_d, subgrade_cbr=5.0)
        assert abs(result.total_thickness_mm - 549.4) <= self._TOL

    def test_case_b_g5(self, fleet_d: TrafficInput) -> None:
        """CBR=12% (G5), 67,500 coverages → 428.7 mm ±25 mm."""
        result = compute_trh14(fleet_d, subgrade_cbr=12.0)
        assert abs(result.total_thickness_mm - 428.7) <= self._TOL

    def test_case_c_g4(self, fleet_d: TrafficInput) -> None:
        """CBR=20% (G4), 67,500 coverages → 287.2 mm ±25 mm."""
        result = compute_trh14(fleet_d, subgrade_cbr=20.0)
        assert abs(result.total_thickness_mm - 287.2) <= self._TOL

    def test_thickness_decreases_with_cbr(self, fleet_d: TrafficInput) -> None:
        """Stronger subgrade → less thickness required."""
        t_g6 = compute_trh14(fleet_d, subgrade_cbr=5.0).total_thickness_mm
        t_g5 = compute_trh14(fleet_d, subgrade_cbr=12.0).total_thickness_mm
        t_g4 = compute_trh14(fleet_d, subgrade_cbr=20.0).total_thickness_mm
        assert t_g6 > t_g5 > t_g4

    def test_thickness_positive(self, fleet_d: TrafficInput) -> None:
        for cbr in [5.0, 12.0, 20.0, 35.0]:
            assert compute_trh14(fleet_d, subgrade_cbr=cbr).total_thickness_mm > 0


# ---------------------------------------------------------------------------
# compute_trh14 — coverage clamping
# ---------------------------------------------------------------------------
class TestComputeTrh14CoverageClamping:
    def test_very_low_coverages_clamped(self) -> None:
        """Very short design life → coverages below catalog minimum, clamped upward."""
        truck = MiningVehicle(
            name="T",
            gross_vehicle_mass_t=10.0,
            axle_groups=[make_single_axle(80.0)],
            source="test",
        )
        # 1 trip/day, 1 year, 10 days → very few coverages
        traffic_low = TrafficInput(
            fleet=[FleetUnit(vehicle=truck, trips_per_day=1)],
            design_life_years=1,
            working_days_per_year=10,
        )
        # Should not raise — coverages are clamped to catalog minimum (100)
        with pytest.warns(UserWarning, match="below catalog minimum"):
            result = compute_trh14(traffic_low, subgrade_cbr=10.0)
        assert result.total_coverages < 100  # confirms input is below catalog min
        assert result.total_thickness_mm == pytest.approx(150.0, abs=1e-6)  # G5 @ min knot

    def test_very_high_coverages_clamped(self) -> None:
        """Extremely heavy traffic → coverages above catalog maximum, clamped downward."""
        truck = MiningVehicle(
            name="T",
            gross_vehicle_mass_t=300.0,
            axle_groups=[make_single_axle(300.0), make_tandem_axle(1200.0)],
            source="test",
        )
        traffic_heavy = TrafficInput(
            fleet=[FleetUnit(vehicle=truck, trips_per_day=100)],
            design_life_years=50,
            working_days_per_year=365,
        )
        with pytest.warns(UserWarning, match="exceed catalog maximum"):
            result = compute_trh14(traffic_heavy, subgrade_cbr=10.0)
        assert result.total_coverages > 1_000_000  # confirms input is above catalog max
        assert result.total_thickness_mm == pytest.approx(600.0, abs=1e-6)  # G5 @ max knot


# ---------------------------------------------------------------------------
# _interpolate_catalog — error handling and edge cases
# ---------------------------------------------------------------------------
class TestInterpolateCatalog:
    """Direct unit tests for the private _interpolate_catalog function."""

    def test_empty_coverage_levels_raises(self) -> None:
        """Empty coverage_levels raises ValueError."""
        with pytest.raises(ValueError, match="must be non-empty"):
            interpolate_catalog([150.0], [], 1000.0)

    def test_empty_thickness_values_raises(self) -> None:
        """Empty thickness_values raises ValueError."""
        with pytest.raises(ValueError, match="must be non-empty"):
            interpolate_catalog([], [100], 1000.0)

    def test_shape_mismatch_raises(self) -> None:
        """Length mismatch raises ValueError."""
        with pytest.raises(ValueError, match="Catalog shape mismatch"):
            interpolate_catalog([150.0, 300.0], [100, 1000, 10000], 1000.0)

    def test_shape_mismatch_with_single_value(self) -> None:
        """Single thickness value with multi-element coverage also raises."""
        with pytest.raises(ValueError, match="Catalog shape mismatch"):
            interpolate_catalog([150.0], [100, 1000, 10000], 1000.0)


# ---------------------------------------------------------------------------
# compute_trh14 — error handling
# ---------------------------------------------------------------------------
class TestComputeTrh14Errors:
    def test_negative_cbr_raises(self, fleet_d: TrafficInput) -> None:
        with pytest.raises(ValueError, match="CBR must be >= 0"):
            compute_trh14(fleet_d, subgrade_cbr=-5.0)

    def test_g8_subgrade_raises(self, fleet_d: TrafficInput) -> None:
        """G8 subgrade (CBR 1.5–1.9%) is not in catalog — requires improvement."""
        with pytest.raises(ValueError, match="G8"):
            compute_trh14(fleet_d, subgrade_cbr=1.7)

    def test_g9_subgrade_raises(self, fleet_d: TrafficInput) -> None:
        """G9 subgrade (CBR < 1.5%) is not in catalog — requires improvement."""
        with pytest.raises(ValueError, match="G9"):
            compute_trh14(fleet_d, subgrade_cbr=0.5)
