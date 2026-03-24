"""Material data models — MaterialLayer.

All thickness fields in mm, strength in kPa or CBR %.

DISCLAIMER: Material property ranges provided as templates are non-normative
guidance values only. Site-specific laboratory testing is required for design.
No liability is accepted for use of template values without independent verification.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


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
