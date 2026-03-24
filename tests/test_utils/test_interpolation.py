"""Tests for PCHIP interpolation utilities."""

from __future__ import annotations

import pytest

from haulpave.utils.interpolation import interpolate_thickness, load_curve_data


@pytest.fixture(scope="module")
def curve_data() -> dict:  # type: ignore[type-arg]
    """Load USACE CBR curve data once for all tests."""
    return load_curve_data("usace_cbr_v1")


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
