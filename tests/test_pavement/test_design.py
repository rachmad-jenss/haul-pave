"""Unit tests for haulpave.pavement.design_pavement.

Tests validate the PavementResult dataclass and the design_pavement() function
across typical inputs covering the full pipeline: CESA → coverages → thickness.
"""

from __future__ import annotations

import pytest

from haulpave.models.material import CustomMaterial
from haulpave.models.traffic import FleetUnit, TrafficInput
from haulpave.models.vehicle import MiningVehicle
from haulpave.pavement import PavementResult, design_pavement

from ..conftest import make_single_axle, make_tandem_axle


@pytest.fixture()
def simple_traffic() -> TrafficInput:
    """A minimal single-vehicle fleet for unit tests."""
    vehicle = MiningVehicle(
        name="Test Truck",
        gross_vehicle_mass_t=100.0,
        axle_groups=[
            make_single_axle(200.0),
            make_tandem_axle(600.0),
        ],
        source="Unit test fixture",
    )
    return TrafficInput(
        fleet=[FleetUnit(vehicle=vehicle, trips_per_day=10)],
        design_life_years=5,
        working_days_per_year=300,
    )


@pytest.fixture()
def fleet_b_traffic() -> TrafficInput:
    """Fleet B — identical to bench_04 fixture (CAT 785D + Motor Grader)."""
    cat_785d = MiningVehicle(
        name="CAT 785D",
        gross_vehicle_mass_t=269.0,
        axle_groups=[
            make_single_axle(225.0),
            make_tandem_axle(1040.0),
        ],
        source="Caterpillar 785D Specifications",
    )
    motor_grader = MiningVehicle(
        name="Motor Grader (25 t)",
        gross_vehicle_mass_t=25.0,
        axle_groups=[
            make_single_axle(85.0),
            make_tandem_axle(160.0),
        ],
        source="Generic motor grader",
    )
    return TrafficInput(
        fleet=[
            FleetUnit(vehicle=cat_785d, trips_per_day=40),
            FleetUnit(vehicle=motor_grader, trips_per_day=5),
        ],
        design_life_years=10,
        working_days_per_year=350,
    )


# ---------------------------------------------------------------------------
# PavementResult dataclass tests
# ---------------------------------------------------------------------------


class TestPavementResult:
    """Tests for the PavementResult frozen dataclass."""

    def test_result_is_frozen(self) -> None:
        """PavementResult must be immutable (frozen=True)."""
        result = PavementResult(
            total_cesa=1_000_000.0,
            total_coverages=5_000.0,
            required_thickness_mm=450.0,
            design_wheel_load_kn=112.5,
        )
        with pytest.raises(AttributeError):
            result.total_cesa = 999.0  # type: ignore[misc]

    def test_result_default_method(self) -> None:
        """Default method string matches USACE TM 5-822-12 reference."""
        result = PavementResult(
            total_cesa=1.0,
            total_coverages=1.0,
            required_thickness_mm=300.0,
            design_wheel_load_kn=80.0,
        )
        assert "USACE TM 5-822-12" in result.method
        assert "AASHTO" in result.method

    def test_result_default_confidence(self) -> None:
        """Default confidence must be 'high'."""
        result = PavementResult(
            total_cesa=1.0,
            total_coverages=1.0,
            required_thickness_mm=300.0,
            design_wheel_load_kn=80.0,
        )
        assert result.confidence == "high"

    def test_result_fields_accessible(self) -> None:
        """All fields are directly accessible on the result."""
        result = PavementResult(
            total_cesa=508_634_682.58,
            total_coverages=530_357.24,
            required_thickness_mm=564.49,
            design_wheel_load_kn=112.5,
            total_thickness_mm=564.49,
            subgrade_cbr=7.0,
        )
        assert result.total_cesa == pytest.approx(508_634_682.58, rel=1e-6)
        assert result.total_coverages == pytest.approx(530_357.24, rel=1e-6)
        assert result.required_thickness_mm == pytest.approx(564.49, rel=1e-6)
        assert result.design_wheel_load_kn == pytest.approx(112.5, rel=1e-6)
        assert result.total_thickness_mm == pytest.approx(564.49, rel=1e-6)
        assert result.subgrade_cbr == pytest.approx(7.0)
        assert result.layers == ()
        assert not result.was_clamped

    def test_total_thickness_mm_matches_required(self) -> None:
        """total_thickness_mm must equal required_thickness_mm."""
        result = PavementResult(
            total_cesa=1.0,
            total_coverages=1.0,
            required_thickness_mm=300.0,
            design_wheel_load_kn=80.0,
            total_thickness_mm=300.0,
        )
        assert result.total_thickness_mm == result.required_thickness_mm

    def test_was_extrapolated_flag_from_design(self, fleet_b_traffic: TrafficInput) -> None:
        """Fleet B coverages (530K) are in the extrapolated zone — was_extrapolated must be True."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = design_pavement(
                traffic=fleet_b_traffic,
                subgrade_cbr=7.0,
                curve_id="usace_cbr_v1",
            )
        assert not result.was_clamped
        assert result.was_extrapolated
        assert result.confidence == "medium"


# ---------------------------------------------------------------------------
# design_pavement() integration tests
# ---------------------------------------------------------------------------


class TestDesignPavement:
    """Integration tests for design_pavement()."""

    def test_returns_pavement_result(self, simple_traffic: TrafficInput) -> None:
        """design_pavement() must return a PavementResult instance."""
        result = design_pavement(
            traffic=simple_traffic,
            subgrade_cbr=5.0,
            curve_id="usace_cbr_v1",
        )
        assert isinstance(result, PavementResult)

    def test_positive_cesa(self, simple_traffic: TrafficInput) -> None:
        """total_cesa must be strictly positive."""
        result = design_pavement(
            traffic=simple_traffic,
            subgrade_cbr=5.0,
            curve_id="usace_cbr_v1",
        )
        assert result.total_cesa > 0.0

    def test_positive_coverages(self, simple_traffic: TrafficInput) -> None:
        """total_coverages must be strictly positive."""
        result = design_pavement(
            traffic=simple_traffic,
            subgrade_cbr=5.0,
            curve_id="usace_cbr_v1",
        )
        assert result.total_coverages > 0.0

    def test_positive_thickness(self, simple_traffic: TrafficInput) -> None:
        """required_thickness_mm must be strictly positive."""
        result = design_pavement(
            traffic=simple_traffic,
            subgrade_cbr=5.0,
            curve_id="usace_cbr_v1",
        )
        assert result.required_thickness_mm > 0.0

    def test_positive_design_wheel_load(self, simple_traffic: TrafficInput) -> None:
        """design_wheel_load_kn must be strictly positive."""
        result = design_pavement(
            traffic=simple_traffic,
            subgrade_cbr=5.0,
            curve_id="usace_cbr_v1",
        )
        assert result.design_wheel_load_kn > 0.0

    def test_invalid_cbr_raises(self, simple_traffic: TrafficInput) -> None:
        """CBR outside curve range must raise ValueError."""
        with pytest.raises(ValueError, match="CBR"):
            design_pavement(
                traffic=simple_traffic,
                subgrade_cbr=0.5,  # below curve minimum
                curve_id="usace_cbr_v1",
            )

    def test_invalid_curve_id_raises(self, simple_traffic: TrafficInput) -> None:
        """Non-existent curve_id must raise FileNotFoundError or similar."""
        with pytest.raises((FileNotFoundError, OSError)):
            design_pavement(
                traffic=simple_traffic,
                subgrade_cbr=5.0,
                curve_id="nonexistent_curve_xyz",
            )

    def test_thickness_decreases_with_cbr(self, simple_traffic: TrafficInput) -> None:
        """Stronger subgrade (higher CBR) must require less thickness."""
        result_soft = design_pavement(
            traffic=simple_traffic,
            subgrade_cbr=3.0,
            curve_id="usace_cbr_v1",
        )
        result_firm = design_pavement(
            traffic=simple_traffic,
            subgrade_cbr=15.0,
            curve_id="usace_cbr_v1",
        )
        assert result_firm.required_thickness_mm < result_soft.required_thickness_mm

    def test_bench04_cesa(self, fleet_b_traffic: TrafficInput) -> None:
        """Fleet B CESA must match bench_04 expected value within 1%."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = design_pavement(
                traffic=fleet_b_traffic,
                subgrade_cbr=7.0,
                curve_id="usace_cbr_v1",
            )
        expected_cesa = 508_634_682.58
        rel_error = abs(result.total_cesa - expected_cesa) / expected_cesa
        assert rel_error <= 0.01, (
            f"CESA: computed={result.total_cesa:.2f}, expected={expected_cesa:.2f}, "
            f"relative error={rel_error:.4%} (tolerance=1%)"
        )

    def test_bench04_coverages(self, fleet_b_traffic: TrafficInput) -> None:
        """Fleet B coverages must match bench_04 expected value within 2%."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = design_pavement(
                traffic=fleet_b_traffic,
                subgrade_cbr=7.0,
                curve_id="usace_cbr_v1",
            )
        expected_coverages = 530_357.24
        rel_error = abs(result.total_coverages - expected_coverages) / expected_coverages
        assert rel_error <= 0.02, (
            f"Coverages: computed={result.total_coverages:.2f}, "
            f"expected={expected_coverages:.2f}, "
            f"relative error={rel_error:.4%} (tolerance=2%)"
        )

    def test_bench04_thickness(self, fleet_b_traffic: TrafficInput) -> None:
        """Fleet B thickness must be greater than the old clamped value.

        Fleet B coverages (530,357) are now in the extrapolated zone (beyond
        100K) rather than clamped. The extrapolated thickness should be greater
        than the 100K-clamped value (564.49 mm).
        """
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = design_pavement(
                traffic=fleet_b_traffic,
                subgrade_cbr=7.0,
                curve_id="usace_cbr_v1",
            )
        assert result.required_thickness_mm > 564.49

    def test_cesa_consistent_with_traffic_module(self, fleet_b_traffic: TrafficInput) -> None:
        """design_pavement CESA must match compute_cesa() called independently."""
        import warnings

        from haulpave.traffic.cesa import compute_cesa

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = design_pavement(
                traffic=fleet_b_traffic,
                subgrade_cbr=7.0,
                curve_id="usace_cbr_v1",
            )
        cesa_direct = compute_cesa(fleet_b_traffic)
        assert result.total_cesa == pytest.approx(cesa_direct.total_cesa, rel=1e-9)

    def test_coverages_consistent_with_traffic_module(self, fleet_b_traffic: TrafficInput) -> None:
        """design_pavement coverages must match compute_coverages() called independently."""
        import warnings

        from haulpave.traffic.coverages import compute_coverages

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = design_pavement(
                traffic=fleet_b_traffic,
                subgrade_cbr=7.0,
                curve_id="usace_cbr_v1",
            )
        cov_direct = compute_coverages(fleet_b_traffic)
        assert result.total_coverages == pytest.approx(cov_direct.total_coverages, rel=1e-9)
        assert result.design_wheel_load_kn == pytest.approx(
            cov_direct.design_wheel_load_kn, rel=1e-9
        )

    def test_custom_materials_populate_layers(self, simple_traffic: TrafficInput) -> None:
        """Custom materials appear as entries in the layers field."""
        import warnings

        materials = [
            CustomMaterial(name="Wearing course", material_type="asphalt", elastic_modulus_mpa=3000.0),
            CustomMaterial(name="Base", material_type="granular", elastic_modulus_mpa=250.0),
        ]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = design_pavement(
                traffic=simple_traffic,
                subgrade_cbr=5.0,
                curve_id="usace_cbr_v1",
                custom_materials=materials,
            )
        assert len(result.layers) == 2
        assert result.layers[0]["name"] == "Wearing course"
        assert result.layers[1]["name"] == "Base"

    def test_custom_materials_hybrid_with_default(self, simple_traffic: TrafficInput) -> None:
        """Design with custom materials still returns valid thickness."""
        import warnings

        mat = CustomMaterial(
            name="Cemented layer",
            material_type="stabilized",
            elastic_modulus_mpa=500.0,
            cbr_percent=60.0,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            result = design_pavement(
                traffic=simple_traffic,
                subgrade_cbr=10.0,
                curve_id="usace_cbr_v1",
                custom_materials=[mat],
            )
        assert result.required_thickness_mm > 0
        assert len(result.layers) == 1
