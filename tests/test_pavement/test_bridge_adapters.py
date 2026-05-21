"""Unit tests for pavement bridge adapter functions.

Tests cbr_thickness_from_coverages and trh14_thickness_from_coverages — the
two thin adapters that accept pre-computed design_coverages instead of a full
TrafficInput (used by haul-calc bridge.py).
"""

from __future__ import annotations

import pytest

from haulpave.pavement import cbr_thickness_from_coverages, trh14_thickness_from_coverages


class TestCbrThicknessFromCoverages:
    def test_returns_positive_thickness(self) -> None:
        t = cbr_thickness_from_coverages(subgrade_cbr=8.0, design_coverages=10_000)
        assert t > 0

    def test_thicker_for_weaker_subgrade(self) -> None:
        strong = cbr_thickness_from_coverages(subgrade_cbr=15.0, design_coverages=10_000)
        weak = cbr_thickness_from_coverages(subgrade_cbr=5.0, design_coverages=10_000)
        assert weak > strong

    def test_thicker_for_more_coverages(self) -> None:
        light = cbr_thickness_from_coverages(subgrade_cbr=8.0, design_coverages=1_000)
        heavy = cbr_thickness_from_coverages(subgrade_cbr=8.0, design_coverages=100_000)
        assert heavy > light

    def test_invalid_coverages_raises(self) -> None:
        with pytest.raises(ValueError):
            cbr_thickness_from_coverages(subgrade_cbr=8.0, design_coverages=0)

    def test_out_of_range_cbr_raises(self) -> None:
        with pytest.raises(ValueError):
            cbr_thickness_from_coverages(subgrade_cbr=200.0, design_coverages=10_000)

    def test_accepts_extrapolated_coverages(self) -> None:
        """Coverages > 100K are accepted without clamping."""
        t = cbr_thickness_from_coverages(subgrade_cbr=8.0, design_coverages=500_000)
        assert t > 0

    def test_extrapolated_thicker_than_digitized(self) -> None:
        """Extrapolated thickness at 500K > thickness at 100K for same CBR."""
        t_100k = cbr_thickness_from_coverages(subgrade_cbr=8.0, design_coverages=100_000)
        t_500k = cbr_thickness_from_coverages(subgrade_cbr=8.0, design_coverages=500_000)
        assert t_500k > t_100k

    def test_coverages_up_to_1m_accepted(self) -> None:
        """Coverages at the new curve max (1M) are accepted."""
        t = cbr_thickness_from_coverages(subgrade_cbr=10.0, design_coverages=1_000_000)
        assert t > 0


class TestTrh14ThicknessFromCoverages:
    def test_returns_result_with_material_class(self) -> None:
        result = trh14_thickness_from_coverages(subgrade_cbr=10.0, design_coverages=10_000)
        assert result.material_class == "G5"
        assert result.total_thickness_mm > 0

    def test_coverages_preserved_in_result(self) -> None:
        result = trh14_thickness_from_coverages(subgrade_cbr=10.0, design_coverages=50_000)
        assert result.total_coverages == 50_000

    def test_thicker_for_weaker_subgrade(self) -> None:
        strong = trh14_thickness_from_coverages(subgrade_cbr=25.0, design_coverages=10_000)
        weak = trh14_thickness_from_coverages(subgrade_cbr=5.0, design_coverages=10_000)
        assert weak.total_thickness_mm > strong.total_thickness_mm

    def test_invalid_coverages_raises(self) -> None:
        with pytest.raises(ValueError, match="design_coverages must be > 0"):
            trh14_thickness_from_coverages(subgrade_cbr=8.0, design_coverages=0)

    def test_very_weak_subgrade_raises(self) -> None:
        with pytest.raises(ValueError, match="G8|G9|subgrade improvement"):
            trh14_thickness_from_coverages(subgrade_cbr=0.5, design_coverages=10_000)

    def test_g1_subgrade(self) -> None:
        result = trh14_thickness_from_coverages(subgrade_cbr=80.0, design_coverages=1_000)
        assert result.material_class == "G1"
