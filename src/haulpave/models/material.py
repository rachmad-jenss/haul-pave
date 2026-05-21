"""Material data models — MaterialLayer, CustomMaterial.

All thickness fields in mm, strength in kPa or CBR %.

DISCLAIMER: Material property ranges provided as templates are non-normative
guidance values only. Site-specific laboratory testing is required for design.
No liability is accepted for use of template values without independent verification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MaterialLayer(BaseModel):
    """A pavement layer material specification.

    When ``is_template`` is True, the properties are indicative ranges from
    published references and must not be used for design without site-specific
    testing (see module-level disclaimer).
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, description="Material name / identifier")
    cbr_percent: float | None = Field(
        default=None, gt=0, description="California Bearing Ratio [%]"
    )
    elastic_modulus_kpa: float | None = Field(
        default=None, gt=0, description="Elastic (resilient) modulus [kPa]"
    )
    thickness_mm: float | None = Field(
        default=None, gt=0, description="Layer thickness [mm]; None if variable/unknown"
    )
    is_template: bool = Field(
        default=False,
        description=(
            "True = indicative reference values only. "
            "NOT for design without independent site testing."
        ),
    )
    source: str | None = Field(
        default=None,
        description="Provenance reference for material properties (required for is_template=True)",
    )

    @model_validator(mode="after")
    def template_requires_source(self) -> MaterialLayer:
        """Enforce that template materials have a provenance source."""
        if self.is_template and not (self.source and self.source.strip()):
            raise ValueError(
                "MaterialLayer with is_template=True must have a non-empty 'source' field. "
                "All template/reference data must be traceable to a published source."
            )
        return self


# ---------------------------------------------------------------------------
# CustomMaterial — user-defined pavement material for thickness design
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CustomMaterial:
    """User-defined pavement material for custom thickness design calculations.

    Allows users to model non-standard materials (crusher run, geocell-stabilised
    layers, cemented base) beyond the built-in catalog.

    Parameters
    ----------
    name:
        Human-readable material name.
    material_type:
        One of ``"granular"``, ``"stabilized"``, ``"asphalt"``, ``"concrete"``.
    elastic_modulus_mpa:
        Elastic (resilient) modulus [MPa].  Must be > 0.
    cbr_percent:
        California Bearing Ratio [%], if applicable (``None`` for bound materials).
    poisson_ratio:
        Poisson's ratio (default 0.35).  Must be in (0, 0.5).
    layer_coefficient:
        AASHTO layer coefficient (structural number per unit thickness), if known.
    thickness_mm:
        Layer thickness [mm], if fixed (``None`` if variable).
    description:
        Optional description or notes.
    """

    name: str
    material_type: Literal["granular", "stabilized", "asphalt", "concrete"]
    elastic_modulus_mpa: float
    cbr_percent: float | None = None
    poisson_ratio: float = 0.35
    layer_coefficient: float | None = None
    thickness_mm: float | None = None
    description: str = ""

    def __post_init__(self) -> None:
        """Validate custom material properties."""
        if self.elastic_modulus_mpa <= 0:
            raise ValueError(
                f"elastic_modulus_mpa must be > 0, got {self.elastic_modulus_mpa}"
            )
        if not (0 < self.poisson_ratio < 0.5):
            raise ValueError(
                f"poisson_ratio must be in (0, 0.5), got {self.poisson_ratio}"
            )


def material_to_layer_coefficient(material: CustomMaterial) -> float:
    """Estimate AASHTO layer coefficient from custom material properties.

    Uses empirical correlation for granular materials (based on CBR) and
    default values for bound materials.

    Parameters
    ----------
    material:
        The custom material to evaluate.

    Returns
    -------
    float
        Estimated layer coefficient (structural number per inch of thickness).

    Notes
    -----
    If ``material.layer_coefficient`` is explicitly set, it is returned directly.
    Otherwise an empirical estimate is computed.
    """
    if material.layer_coefficient is not None:
        return material.layer_coefficient

    if material.material_type in ("asphalt", "concrete"):
        return 0.44

    if material.material_type == "stabilized":
        return 0.23

    # Granular: empirical correlation from CBR
    cbr = material.cbr_percent
    if cbr is not None and cbr >= 80:
        return 0.14
    elif cbr is not None and cbr >= 50:
        return 0.13
    elif cbr is not None and cbr >= 30:
        return 0.12
    elif cbr is not None and cbr >= 15:
        return 0.11
    elif cbr is not None and cbr >= 7:
        return 0.10
    else:
        return 0.08
