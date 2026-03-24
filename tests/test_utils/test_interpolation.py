"""Tests for PCHIP interpolation utilities."""

from __future__ import annotations

import pytest

from haulpave.utils.interpolation import (
    _validate_curve_data,
    interpolate_thickness,
    load_curve_data,
)


@pytest.fixture(scope="module")
def curve_data() -> dict:  # type: ignore[type-arg]
    """Load USACE CBR curve data once for all tests."""
    return load_curve_data("usace_cbr_v1")


class TestValidateCurveData:
    def test_raises_on_missing_keys(self) -> None:
        """Missing required keys raises ValueError."""
        with pytest.raises(ValueError, match="missing required keys"):
            _validate_curve_data({"cbr_values": [1, 2]})

    def test_raises_on_length_mismatch(self) -> None:
        """thickness_mm array length mismatch raises ValueError."""
        bad_data: dict = {
            "cbr_values": [2, 10, 100],
            "coverage_levels": [100, 1000],
            "thickness_mm": {
                "100": [600, 400],  # only 2 values, needs 3
                "1000": [700, 500],  # only 2 values, needs 3
            },
        }
        with pytest.raises(ValueError, match="thickness_mm"):
            _validate_curve_data(bad_data)

    def test_raises_on_missing_coverage_key(self) -> None:
        """Missing coverage key in thickness_mm raises ValueError."""
        bad_data: dict = {
            "cbr_values": [2, 100],
            "coverage_levels": [100, 1000],
            "thickness_mm": {"100": [600, 150]},  # missing "1000"
        }
        with pytest.raises(ValueError, match="missing coverage level key"):
            _validate_curve_data(bad_data)


class TestLoadCurveData:
    def test_returns_dict_with_expected_keys(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        expected_keys = {
            "schema_version",
            "curve_id",
            "description",
            "x_axis",
            "y_axis",
            "parameter",
            "coverage_levels",
            "cbr_values",
            "thickness_mm",
        }
        assert expected_keys.issubset(curve_data.keys())

    def test_curve_id_matches(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        assert curve_data["curve_id"] == "usace_cbr_v1"

    def test_coverage_levels_count(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        assert len(curve_data["coverage_levels"]) == 9

    def test_cbr_values_count(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        assert len(curve_data["cbr_values"]) == 14


class TestInterpolateThickness:
    def test_cbr10_coverages1000_approx_408mm(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """Benchmark: CBR=10, coverages=1000 -> ~408 mm (+-5 mm)."""
        result = interpolate_thickness(curve_data, cbr=10, coverages=1000)
        assert abs(result - 408.0) <= 5.0, f"Expected ~408 mm, got {result:.1f} mm"

    def test_cbr5_coverages100_approx_462mm(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """Benchmark: CBR=5, coverages=100 -> ~462 mm (+-5 mm)."""
        result = interpolate_thickness(curve_data, cbr=5, coverages=100)
        assert abs(result - 462.0) <= 5.0, f"Expected ~462 mm, got {result:.1f} mm"

    def test_monotonicity_higher_cbr_lower_thickness(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """Higher CBR -> lower required thickness (same coverages)."""
        cbr_values = [5, 10, 20, 30, 50]
        thicknesses = [
            interpolate_thickness(curve_data, cbr=cbr, coverages=1000) for cbr in cbr_values
        ]
        for i in range(len(thicknesses) - 1):
            assert thicknesses[i] > thicknesses[i + 1], (
                f"Expected thickness to decrease: CBR {cbr_values[i]} -> "
                f"{thicknesses[i]:.1f} mm, CBR {cbr_values[i + 1]} -> "
                f"{thicknesses[i + 1]:.1f} mm"
            )

    def test_monotonicity_higher_coverages_higher_thickness(
        self,
        curve_data: dict,  # type: ignore[type-arg]
    ) -> None:
        """Higher coverages -> higher required thickness (same CBR)."""
        coverage_values = [100, 1000, 10000, 100000]
        thicknesses = [
            interpolate_thickness(curve_data, cbr=10, coverages=cov) for cov in coverage_values
        ]
        for i in range(len(thicknesses) - 1):
            assert thicknesses[i] < thicknesses[i + 1], (
                f"Expected thickness to increase: coverages {coverage_values[i]} -> "
                f"{thicknesses[i]:.1f} mm, coverages {coverage_values[i + 1]} -> "
                f"{thicknesses[i + 1]:.1f} mm"
            )

    def test_raises_value_error_cbr_below_range(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """CBR below minimum (< 2) raises ValueError."""
        with pytest.raises(ValueError, match="CBR"):
            interpolate_thickness(curve_data, cbr=1, coverages=1000)

    def test_raises_value_error_cbr_above_range(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """CBR above maximum (> 100) raises ValueError."""
        with pytest.raises(ValueError, match="CBR"):
            interpolate_thickness(curve_data, cbr=101, coverages=1000)

    def test_boundary_cbr_min(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """CBR=2 (minimum boundary) works without error."""
        result = interpolate_thickness(curve_data, cbr=2, coverages=1000)
        assert result > 0

    def test_boundary_cbr_max(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """CBR=100 (maximum boundary) works without error."""
        result = interpolate_thickness(curve_data, cbr=100, coverages=1000)
        assert result > 0

    def test_raises_value_error_zero_coverages(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """Zero coverages raises ValueError."""
        with pytest.raises(ValueError, match="coverages"):
            interpolate_thickness(curve_data, cbr=10, coverages=0)

    def test_raises_value_error_negative_coverages(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """Negative coverages raises ValueError."""
        with pytest.raises(ValueError, match="coverages"):
            interpolate_thickness(curve_data, cbr=10, coverages=-1)

    def test_coverages_below_min_clamps_to_min_level(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """Coverages below curve minimum are clamped to minimum coverage level (10)."""
        result_clamped = interpolate_thickness(curve_data, cbr=10, coverages=1)
        result_min = interpolate_thickness(curve_data, cbr=10, coverages=10)
        assert result_clamped == result_min, (
            f"Expected coverages=1 to clamp to coverages=10: "
            f"got {result_clamped:.1f} vs {result_min:.1f} mm"
        )

    def test_coverages_above_max_clamps_to_max_level(self, curve_data: dict) -> None:  # type: ignore[type-arg]
        """Coverages above curve maximum are clamped to maximum coverage level (100000)."""
        result_clamped = interpolate_thickness(curve_data, cbr=10, coverages=1_000_000)
        result_max = interpolate_thickness(curve_data, cbr=10, coverages=100_000)
        assert result_clamped == result_max, (
            f"Expected coverages=1_000_000 to clamp to coverages=100_000: "
            f"got {result_clamped:.1f} vs {result_max:.1f} mm"
        )
