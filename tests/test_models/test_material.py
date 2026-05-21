"""Tests for haulpave.models.material."""

import pytest
from pydantic import ValidationError

from haulpave.models.material import (
    CustomMaterial,
    MaterialLayer,
    material_to_layer_coefficient,
)


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

    def test_template_with_whitespace_only_source_rejected(self) -> None:
        with pytest.raises(ValidationError, match="is_template"):
            MaterialLayer(name="Gravel", is_template=True, source="   ")

    def test_immutable(self) -> None:
        layer = MaterialLayer(name="Base")
        with pytest.raises(ValidationError):
            layer.name = "Other"  # type: ignore[misc]


class TestCustomMaterial:
    def test_minimal_valid(self) -> None:
        m = CustomMaterial(
            name="Crusher run",
            material_type="granular",
            elastic_modulus_mpa=250.0,
        )
        assert m.name == "Crusher run"
        assert m.poisson_ratio == 0.35
        assert m.cbr_percent is None

    def test_full_valid(self) -> None:
        m = CustomMaterial(
            name="Cemented base",
            material_type="stabilized",
            elastic_modulus_mpa=500.0,
            cbr_percent=60.0,
            poisson_ratio=0.30,
            layer_coefficient=0.18,
            thickness_mm=200.0,
            description="Cement-stabilised crushed rock",
        )
        assert m.thickness_mm == 200.0

    def test_zero_modulus_raises(self) -> None:
        with pytest.raises(ValueError, match="elastic_modulus_mpa"):
            CustomMaterial(
                name="Bad",
                material_type="granular",
                elastic_modulus_mpa=0,
            )

    def test_negative_modulus_raises(self) -> None:
        with pytest.raises(ValueError, match="elastic_modulus_mpa"):
            CustomMaterial(
                name="Bad",
                material_type="granular",
                elastic_modulus_mpa=-10,
            )

    def test_poisson_ratio_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="poisson_ratio"):
            CustomMaterial(
                name="Bad",
                material_type="granular",
                elastic_modulus_mpa=100.0,
                poisson_ratio=0.0,
            )

    def test_poisson_ratio_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="poisson_ratio"):
            CustomMaterial(
                name="Bad",
                material_type="granular",
                elastic_modulus_mpa=100.0,
                poisson_ratio=-0.1,
            )

    def test_poisson_ratio_half_raises(self) -> None:
        with pytest.raises(ValueError, match="poisson_ratio"):
            CustomMaterial(
                name="Bad",
                material_type="granular",
                elastic_modulus_mpa=100.0,
                poisson_ratio=0.5,
            )

    def test_immutable(self) -> None:
        m = CustomMaterial(
            name="Test",
            material_type="granular",
            elastic_modulus_mpa=100.0,
        )
        with pytest.raises(AttributeError):
            m.name = "Changed"  # type: ignore[misc]


class TestMaterialToLayerCoefficient:
    def test_explicit_coefficient_returned(self) -> None:
        m = CustomMaterial(
            name="Base",
            material_type="granular",
            elastic_modulus_mpa=200.0,
            layer_coefficient=0.15,
        )
        assert material_to_layer_coefficient(m) == 0.15

    def test_asphalt_default(self) -> None:
        m = CustomMaterial(
            name="AC",
            material_type="asphalt",
            elastic_modulus_mpa=3000.0,
        )
        assert material_to_layer_coefficient(m) == 0.44

    def test_concrete_default(self) -> None:
        m = CustomMaterial(
            name="PCC",
            material_type="concrete",
            elastic_modulus_mpa=30000.0,
        )
        assert material_to_layer_coefficient(m) == 0.44

    def test_stabilized_default(self) -> None:
        m = CustomMaterial(
            name="Cemented",
            material_type="stabilized",
            elastic_modulus_mpa=500.0,
        )
        assert material_to_layer_coefficient(m) == 0.23

    def test_granular_high_cbr(self) -> None:
        m = CustomMaterial(
            name="G1 rock",
            material_type="granular",
            elastic_modulus_mpa=400.0,
            cbr_percent=80.0,
        )
        assert material_to_layer_coefficient(m) == 0.14

    def test_granular_medium_cbr(self) -> None:
        m = CustomMaterial(
            name="G5 gravel",
            material_type="granular",
            elastic_modulus_mpa=120.0,
            cbr_percent=10.0,
        )
        assert material_to_layer_coefficient(m) == 0.10

    def test_granular_low_cbr(self) -> None:
        m = CustomMaterial(
            name="Silty sand",
            material_type="granular",
            elastic_modulus_mpa=50.0,
            cbr_percent=3.0,
        )
        assert material_to_layer_coefficient(m) == 0.08
