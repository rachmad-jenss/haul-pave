"""Tests for haulpave.models.material."""

import pytest
from pydantic import ValidationError

from haulpave.models.material import MaterialLayer


class TestMaterialLayer:
    def test_minimal_valid(self) -> None:
        layer = MaterialLayer(name="Crushed rock base")
        assert layer.cbr_percent is None
        assert layer.is_template is False

    def test_full_valid(self) -> None:
        layer = MaterialLayer(
            name="Compacted gravel",
            cbr_percent=80.0,
            elastic_modulus_kpa=150_000.0,
            thickness_mm=300.0,
            is_template=True,
            source="ARRB Guide 2013, Table 4.2",
        )
        assert layer.thickness_mm == 300.0
        assert layer.is_template is True

    def test_zero_cbr_rejected(self) -> None:
        with pytest.raises(ValidationError):
            MaterialLayer(name="X", cbr_percent=0.0)

    def test_negative_thickness_rejected(self) -> None:
        with pytest.raises(ValidationError):
            MaterialLayer(name="X", thickness_mm=-10.0)

    def test_template_without_source_rejected(self) -> None:
        with pytest.raises(ValidationError, match="is_template"):
            MaterialLayer(name="Gravel", is_template=True)

    def test_template_with_source_accepted(self) -> None:
        layer = MaterialLayer(name="Gravel", is_template=True, source="TRH 14 Table 2")
        assert layer.is_template is True
        assert layer.source == "TRH 14 Table 2"

    def test_non_template_without_source_accepted(self) -> None:
        layer = MaterialLayer(name="Site gravel")
        assert layer.is_template is False
        assert layer.source is None

    def test_immutable(self) -> None:
        layer = MaterialLayer(name="Base")
        with pytest.raises(ValidationError):
            layer.name = "Other"  # type: ignore[misc]
