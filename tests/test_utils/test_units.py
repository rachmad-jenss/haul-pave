"""Unit tests for haulpave.utils.units."""

from __future__ import annotations

import pytest

from haulpave.utils import units


class TestPressure:
    def test_psi_to_kpa_known_value(self) -> None:
        assert units.psi_to_kpa(100.0) == pytest.approx(689.4757293168)

    def test_kpa_to_psi_known_value(self) -> None:
        assert units.kpa_to_psi(689.476) == pytest.approx(100.0, rel=1e-4)

    def test_psi_kpa_roundtrip(self) -> None:
        for val in (0.0, 1.0, 14.7, 100.0, 1000.0):
            assert units.psi_to_kpa(units.kpa_to_psi(val)) == pytest.approx(val, rel=1e-6)

    def test_psi_to_kpa_zero(self) -> None:
        assert units.psi_to_kpa(0.0) == 0.0

    def test_kpa_to_psi_zero(self) -> None:
        assert units.kpa_to_psi(0.0) == 0.0

    def test_psi_to_kpa_negative(self) -> None:
        assert units.psi_to_kpa(-10.0) < 0.0


class TestMass:
    def test_tons_to_tonnes_known(self) -> None:
        assert units.tons_to_tonnes(1.0) == pytest.approx(0.907185)

    def test_tonnes_to_tons_known(self) -> None:
        assert units.tonnes_to_tons(0.907185) == pytest.approx(1.0, rel=1e-5)

    def test_tons_tonnes_roundtrip(self) -> None:
        for val in (0.0, 1.0, 50.0, 400.0):
            assert units.tons_to_tonnes(units.tonnes_to_tons(val)) == pytest.approx(val, rel=1e-6)

    def test_lbs_to_kg_known(self) -> None:
        assert units.lbs_to_kg(2.20462) == pytest.approx(1.0, rel=1e-4)

    def test_lbs_to_kg_zero(self) -> None:
        assert units.lbs_to_kg(0.0) == 0.0


class TestLength:
    def test_inches_to_mm_known(self) -> None:
        assert units.inches_to_mm(1.0) == 25.4

    def test_mm_to_inches_known(self) -> None:
        assert units.mm_to_inches(25.4) == 1.0

    def test_inches_mm_roundtrip(self) -> None:
        for val in (0.0, 1.0, 12.0, 36.0):
            assert units.inches_to_mm(units.mm_to_inches(val)) == pytest.approx(val)

    def test_feet_to_m_known(self) -> None:
        assert units.feet_to_m(1.0) == 0.3048

    def test_feet_to_m_zero(self) -> None:
        assert units.feet_to_m(0.0) == 0.0


class TestArea:
    def test_sq_inches_to_cm2_known(self) -> None:
        assert units.sq_inches_to_cm2(1.0) == 6.4516

    def test_sq_feet_to_m2_known(self) -> None:
        assert units.sq_feet_to_m2(1.0) == pytest.approx(0.092903)

    def test_sq_in_cm2_roundtrip(self) -> None:
        for val in (0.0, 1.0, 100.0):
            assert units.sq_inches_to_cm2(val) / 6.4516 == pytest.approx(val)

    def test_sq_feet_m2_roundtrip(self) -> None:
        for val in (0.0, 1.0, 100.0):
            assert units.sq_feet_to_m2(val) / 0.092903 == pytest.approx(val)


class TestForce:
    def test_lbf_to_kn_known(self) -> None:
        assert units.lbf_to_kn(224.809) == pytest.approx(1.0, rel=1e-4)

    def test_kn_to_lbf_known(self) -> None:
        assert units.kn_to_lbf(1.0) == pytest.approx(224.809, rel=1e-4)

    def test_lbf_kn_roundtrip(self) -> None:
        for val in (0.0, 1.0, 10.0, 100.0):
            assert units.lbf_to_kn(units.kn_to_lbf(val)) == pytest.approx(val, rel=1e-6)

    def test_lbf_to_kn_zero(self) -> None:
        assert units.lbf_to_kn(0.0) == 0.0


class TestSpeed:
    def test_mph_to_kmh_known(self) -> None:
        assert units.mph_to_kmh(60.0) == pytest.approx(96.56064)

    def test_kmh_to_mph_known(self) -> None:
        assert units.kmh_to_mph(100.0) == pytest.approx(62.1371, rel=1e-4)

    def test_mph_kmh_roundtrip(self) -> None:
        for val in (0.0, 10.0, 30.0, 55.0, 70.0):
            assert units.mph_to_kmh(units.kmh_to_mph(val)) == pytest.approx(val, rel=1e-6)

    def test_negative_speed(self) -> None:
        assert units.mph_to_kmh(-10.0) < 0.0


class TestAllExports:
    def test_all_contains_eighteen_functions(self) -> None:
        assert len(units.__all__) == 18

    def test_all_exports_are_callable(self) -> None:
        for name in units.__all__:
            func = getattr(units, name)
            assert callable(func), f"{name} is not callable"
