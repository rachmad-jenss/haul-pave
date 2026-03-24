"""Pavement design data models — SubgradeInfo, PavementStructure, DesignResult.

All thickness fields in mm, strength in kPa or CBR %.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from haulpave.models.material import MaterialLayer


class SubgradeInfo(BaseModel):
    """Subgrade characterisation for pavement design."""

    model_config = ConfigDict(frozen=True)

    cbr_percent: float = Field(gt=0, description="In-situ subgrade CBR [%]")
    description: str | None = Field(default=None, description="Soil description or USCS class")
    source: str | None = Field(default=None, description="Test report or reference")


class PavementStructure(BaseModel):
    """Full pavement layer stack (surface → subgrade)."""

    model_config = ConfigDict(frozen=True)

    layers: list[MaterialLayer] = Field(
        min_length=1,
        description="Ordered layers, surface first",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_thickness_mm(self) -> float:
        """Sum of all layer thicknesses that are explicitly specified."""
        return sum(layer.thickness_mm for layer in self.layers if layer.thickness_mm is not None)


class DesignResult(BaseModel):
    """Output of a pavement thickness design calculation.

    Confidence labels follow the project plan convention:
    - ``benchmark_tested``: result matches a published hand-calculation benchmark
    - ``method_implemented``: code faithfully implements the published method
    - ``experimental``: adaptation or extension not yet benchmark-tested
    """

    model_config = ConfigDict(frozen=True)

    pavement_structure: PavementStructure
    subgrade: SubgradeInfo
    design_coverages: float = Field(ge=0, description="Design coverages used")
    confidence: Literal["benchmark_tested", "method_implemented", "experimental"] = Field(
        description="Confidence label per project plan §4.3"
    )

    # Versioning / audit fields
    method_id: str = Field(
        min_length=1,
        description="Calculation method identifier, e.g. 'USACE-TM5-822-12'",
    )
    package_version: str = Field(
        min_length=1,
        description="haulpave package version that produced this result",
    )
    curve_version: str | None = Field(
        default=None, description="Curve digitization version, if applicable"
    )
    input_hash: str | None = Field(
        default=None,
        pattern=r"^[a-fA-F0-9]{64}$",
        description="SHA-256 hex digest of serialised inputs",
    )
