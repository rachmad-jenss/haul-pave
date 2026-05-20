"""Tests for haulpave.models.pavement."""

import pytest
from pydantic import ValidationError

from haulpave.models.material import MaterialLayer
from haulpave.models.pavement import DesignResult, PavementStructure, SubgradeInfo


@pytest.fixture()
def layers() -> list[MaterialLayer]:
    return [
        MaterialLayer(name="Wearing course", thickness_mm=100.0),
        MaterialLayer(name="Base course", thickness_mm=200.0),
        MaterialLayer(name="Subbase", thickness_mm=300.0),
    ]


@pytest.fixture()
def structure(layers: list[MaterialLayer]) -> PavementStructure:
    return PavementStructure(layers=layers)


@pytest.fixture()
def subgrade() -> SubgradeInfo:
    return SubgradeInfo(cbr_percent=5.0, description="Silty clay")


class TestSubgradeInfo:
    def test_valid(self, subgrade: SubgradeInfo) -> None:
        assert subgrade.cbr_percent == 5.0

    def test_zero_cbr_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SubgradeInfo(cbr_percent=0.0)


class TestPavementStructure:
    def test_total_thickness(self, structure: PavementStructure) -> None:
        assert structure.total_thickness_mm == pytest.approx(600.0)

    def test_partial_thickness(self) -> None:
        layers = [
            MaterialLayer(name="Wearing course", thickness_mm=100.0),
            MaterialLayer(name="Base (unknown thickness)"),  # no thickness
        ]
        ps = PavementStructure(layers=layers)
        assert ps.total_thickness_mm == pytest.approx(100.0)

    def test_empty_layers_rejected(self) -> None:
        with pytest.raises(ValidationError):
            PavementStructure(layers=[])


class TestDesignResult:
    def test_valid(self, structure: PavementStructure, subgrade: SubgradeInfo) -> None:
        dr = DesignResult(
            pavement_structure=structure,
            subgrade=subgrade,
            design_coverages=1500.0,
            confidence="high",
            method_id="USACE-TM5-822-12",
            package_version="0.0.1",
        )
        assert dr.confidence == "high"
        assert dr.curve_version is None
        assert dr.input_hash is None

    def test_invalid_confidence_rejected(
        self, structure: PavementStructure, subgrade: SubgradeInfo
    ) -> None:
        with pytest.raises(ValidationError):
            DesignResult(
                pavement_structure=structure,
                subgrade=subgrade,
                design_coverages=1500.0,
                confidence="unknown_label",  # type: ignore[arg-type]
                method_id="USACE-TM5-822-12",
                package_version="0.0.1",
            )

    def test_all_confidence_literals(
        self, structure: PavementStructure, subgrade: SubgradeInfo
    ) -> None:
        for label in ("high", "medium", "low"):
            dr = DesignResult(
                pavement_structure=structure,
                subgrade=subgrade,
                design_coverages=100.0,
                confidence=label,  # type: ignore[arg-type]
                method_id="test",
                package_version="0.0.1",
            )
            assert dr.confidence == label
