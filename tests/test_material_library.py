"""Unit tests for material_library."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from haulpave.material_library import (
    MATERIAL_CATALOG,
    MaterialTemplate,
    find_by_cbr,
    find_by_class,
    list_all,
)


class TestListAll:
    def test_returns_sixteen_templates(self) -> None:
        templates = list_all()
        assert len(templates) == 16

    def test_all_are_material_templates(self) -> None:
        for t in list_all():
            assert isinstance(t, MaterialTemplate)

    def test_contains_trh14_and_usace_entries(self) -> None:
        classes = {t.material_class for t in list_all()}
        assert "G1" in classes
        assert "N/A" in classes
        assert len(classes) == 10  # G1-G9 + N/A

    def test_immutable(self) -> None:
        t = list_all()[0]
        with pytest.raises(ValidationError):
            t.name = "changed"  # type: ignore[misc]


class TestFindByClass:
    def test_g1_through_g9(self) -> None:
        for g in ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9"]:
            result = find_by_class(g)
            assert result is not None, f"G-class {g} should exist"
            assert result.material_class == g

    def test_na_returns_none(self) -> None:
        assert find_by_class("N/A") is None

    def test_invalid_class_returns_none(self) -> None:
        assert find_by_class("G10") is None
        assert find_by_class("FOO") is None
        assert find_by_class("") is None

    def test_returns_material_template_type(self) -> None:
        result = find_by_class("G5")
        assert isinstance(result, MaterialTemplate)


class TestFindByCbr:
    def test_g1_boundary_cbr_80(self) -> None:
        results = find_by_cbr(80.0)
        g_classes = {r.material_class for r in results}
        assert "G1" in g_classes
        assert "G2" not in g_classes

    def test_g5_range_cbr_10(self) -> None:
        results = find_by_cbr(10.0)
        g_classes = {r.material_class for r in results}
        assert "G5" in g_classes
        assert "G4" not in g_classes

    def test_cbr_50_matches_g2_and_usace(self) -> None:
        results = find_by_cbr(50.0)
        g_classes = {r.material_class for r in results}
        assert "G2" in g_classes
        assert "N/A" in g_classes

    def test_cbr_3_matches_g7(self) -> None:
        results = find_by_cbr(3.0)
        g_classes = {r.material_class for r in results}
        assert "G7" in g_classes

    def test_cbr_zero_matches_g9(self) -> None:
        results = find_by_cbr(0.0)
        g_classes = {r.material_class for r in results}
        assert "G9" in g_classes

    def test_cbr_1_point_5_matches_g8(self) -> None:
        results = find_by_cbr(1.5)
        g_classes = {r.material_class for r in results}
        assert "G8" in g_classes

    def test_cbr_negative_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="CBR must be >= 0"):
            find_by_cbr(-1.0)

    def test_cbr_below_g9_range_still_matches_g9(self) -> None:
        results = find_by_cbr(0.5)
        g_classes = {r.material_class for r in results}
        assert "G9" in g_classes

    def test_cbr_100_matches_g1(self) -> None:
        results = find_by_cbr(100.0)
        g_classes = {r.material_class for r in results}
        assert "G1" in g_classes

    def test_returns_material_templates(self) -> None:
        results = find_by_cbr(12.0)
        for r in results:
            assert isinstance(r, MaterialTemplate)

    def test_cbr_above_100_g1_only(self) -> None:
        results = find_by_cbr(150.0)
        g_classes = {r.material_class for r in results}
        assert g_classes == {"G1"}

    def test_cbr_100_excludes_usace_boundary(self) -> None:
        results = find_by_cbr(100.0)
        g_classes = {r.material_class for r in results}
        assert "G1" in g_classes
        assert "N/A" not in g_classes


class TestMaterialCatalog:
    def test_catalog_has_sixteen_entries(self) -> None:
        assert len(MATERIAL_CATALOG) == 16

    def test_trh14_count_is_nine(self) -> None:
        trh14 = [t for t in MATERIAL_CATALOG if t.material_class.startswith("G")]
        assert len(trh14) == 9

    def test_usace_count_is_seven(self) -> None:
        usace = [t for t in MATERIAL_CATALOG if t.material_class == "N/A"]
        assert len(usace) == 7

    def test_all_have_source(self) -> None:
        for t in MATERIAL_CATALOG:
            assert t.source, f"{t.name} missing source"
            assert len(t.source) > 5

    def test_all_have_positive_modulus(self) -> None:
        for t in MATERIAL_CATALOG:
            assert t.typical_modulus_mpa > 0


class TestMaterialTemplateValidation:
    def test_negative_cbr_lower_bound_rejected(self) -> None:
        with pytest.raises(ValidationError):
            MaterialTemplate(
                name="Bad",
                material_class="G1",
                cbr_range=(-1.0, 10.0),
                typical_modulus_mpa=100.0,
                source="Test source",
            )

    def test_upper_bound_not_greater_than_lower_rejected(self) -> None:
        with pytest.raises(ValidationError):
            MaterialTemplate(
                name="Bad",
                material_class="G1",
                cbr_range=(10.0, 5.0),
                typical_modulus_mpa=100.0,
                source="Test source",
            )
