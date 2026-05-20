"""Material library — normative material property templates for haul-pave.

Provides ``MaterialTemplate`` models and a built-in ``MATERIAL_CATALOG``
seeded with TRH 14 G-class materials (CSRA 1985) and USACE TM 5-822-12
typical materials.

IMPORTANT: These are convenience templates for early-stage analysis and
education. They are NOT normative design values — site-specific testing
is required before use in real projects.

Confidence label: ``method_implemented``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "MaterialTemplate",
    "MATERIAL_CATALOG",
    "find_by_cbr",
    "find_by_class",
    "list_all",
]


class MaterialTemplate(BaseModel):
    """A template for a common pavement material with normative reference values.

    Attributes
    ----------
    name:
        Human-readable material name, e.g. ``"Crushed rock base (G1)"``.
    material_class:
        TRH 14 G-class (G1–G9) or ``"N/A"`` for non-G-class materials.
    cbr_range:
        Inclusive lower and exclusive upper CBR bounds ``(min, max)`` [%].
        The upper bound is ``None`` when unbounded (e.g. G1: CBR ≥ 80).
    typical_modulus_mpa:
        Typical elastic (resilient) modulus [MPa] for the material class.
    source:
        Provenance reference for the template data.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, description="Material name / identifier")
    material_class: str = Field(description="TRH 14 G-class (G1–G9) or 'N/A'")
    cbr_range: tuple[float, float | None] = Field(
        description="(min, max) CBR bounds [%]; None = unbounded upper"
    )
    typical_modulus_mpa: float = Field(gt=0, description="Typical elastic modulus [MPa]")
    source: str = Field(min_length=1, description="Provenance reference for template data")


# ---------------------------------------------------------------------------
# TRH 14 G-class materials (CSRA 1985, Table 2)
# ---------------------------------------------------------------------------
# CBR boundaries derived from trh14.py _G_CLASS_BOUNDS:
#   G1≥80, G2≥45, G3≥25, G4≥15, G5≥7, G6≥4, G7≥2, G8≥1.5, G9≥0
# Modulus values are typical per G-class from CSRA (1985) / TRH 14.

_TRH14_TEMPLATES: list[MaterialTemplate] = [
    MaterialTemplate(
        name="Very high quality crushed rock (G1)",
        material_class="G1",
        cbr_range=(80.0, None),
        typical_modulus_mpa=500.0,
        source="CSRA TRH 14 (1985), Table 2; modulus: CSRA (1985) §4.3",
    ),
    MaterialTemplate(
        name="High quality crushed rock (G2)",
        material_class="G2",
        cbr_range=(45.0, 80.0),
        typical_modulus_mpa=400.0,
        source="CSRA TRH 14 (1985), Table 2; modulus: CSRA (1985) §4.3",
    ),
    MaterialTemplate(
        name="Good quality crushed rock (G3)",
        material_class="G3",
        cbr_range=(25.0, 45.0),
        typical_modulus_mpa=300.0,
        source="CSRA TRH 14 (1985), Table 2; modulus: CSRA (1985) §4.3",
    ),
    MaterialTemplate(
        name="Natural gravel (G4)",
        material_class="G4",
        cbr_range=(15.0, 25.0),
        typical_modulus_mpa=200.0,
        source="CSRA TRH 14 (1985), Table 2; modulus: CSRA (1985) §4.3",
    ),
    MaterialTemplate(
        name="Gravel-sand mix (G5)",
        material_class="G5",
        cbr_range=(7.0, 15.0),
        typical_modulus_mpa=120.0,
        source="CSRA TRH 14 (1985), Table 2; modulus: CSRA (1985) §4.3",
    ),
    MaterialTemplate(
        name="Sandy soil (G6)",
        material_class="G6",
        cbr_range=(4.0, 7.0),
        typical_modulus_mpa=65.0,
        source="CSRA TRH 14 (1985), Table 2; modulus: CSRA (1985) §4.3",
    ),
    MaterialTemplate(
        name="Low CBR soil (G7)",
        material_class="G7",
        cbr_range=(2.0, 4.0),
        typical_modulus_mpa=40.0,
        source="CSRA TRH 14 (1985), Table 2; modulus: CSRA (1985) §4.3",
    ),
    MaterialTemplate(
        name="Very low CBR soil (G8)",
        material_class="G8",
        cbr_range=(1.5, 2.0),
        typical_modulus_mpa=25.0,
        source="CSRA TRH 14 (1985), Table 2; modulus: CSRA (1985) §4.3",
    ),
    MaterialTemplate(
        name="Extremely low CBR soil (G9)",
        material_class="G9",
        cbr_range=(0.0, 1.5),
        typical_modulus_mpa=10.0,
        source="CSRA TRH 14 (1985), Table 2; modulus: CSRA (1985) §4.3",
    ),
]

# ---------------------------------------------------------------------------
# USACE TM 5-822-12 typical materials
# ---------------------------------------------------------------------------
_USACE_TEMPLATES: list[MaterialTemplate] = [
    MaterialTemplate(
        name="Crushed stone base (high quality)",
        material_class="N/A",
        cbr_range=(80.0, 100.0),
        typical_modulus_mpa=450.0,
        source="USACE TM 5-822-12 (1990), Table 2-1",
    ),
    MaterialTemplate(
        name="Gravel base (well-graded)",
        material_class="N/A",
        cbr_range=(50.0, 80.0),
        typical_modulus_mpa=250.0,
        source="USACE TM 5-822-12 (1990), Table 2-1",
    ),
    MaterialTemplate(
        name="Sand subbase",
        material_class="N/A",
        cbr_range=(10.0, 30.0),
        typical_modulus_mpa=80.0,
        source="USACE TM 5-822-12 (1990), Table 2-1",
    ),
    MaterialTemplate(
        name="Selected fill (compacted)",
        material_class="N/A",
        cbr_range=(5.0, 15.0),
        typical_modulus_mpa=50.0,
        source="USACE TM 5-822-12 (1990), §3-2",
    ),
    MaterialTemplate(
        name="Silty subgrade",
        material_class="N/A",
        cbr_range=(2.0, 5.0),
        typical_modulus_mpa=30.0,
        source="USACE TM 5-822-12 (1990), Table 3-1",
    ),
    MaterialTemplate(
        name="Clay subgrade (low plasticity)",
        material_class="N/A",
        cbr_range=(1.0, 3.0),
        typical_modulus_mpa=15.0,
        source="USACE TM 5-822-12 (1990), Table 3-1",
    ),
    MaterialTemplate(
        name="Clay subgrade (high plasticity)",
        material_class="N/A",
        cbr_range=(0.5, 1.5),
        typical_modulus_mpa=8.0,
        source="USACE TM 5-822-12 (1990), Table 3-1",
    ),
]

MATERIAL_CATALOG: list[MaterialTemplate] = _TRH14_TEMPLATES + _USACE_TEMPLATES
"""Built-in material property templates.

Includes entries from:
- TRH 14 G-class materials (CSRA 1985)
- USACE TM 5-822-12 typical materials
"""


def find_by_cbr(cbr: float) -> list[MaterialTemplate]:
    """Return all templates whose CBR range contains the given value.

    Parameters
    ----------
    cbr:
        California Bearing Ratio [%]. Must be ≥ 0.

    Returns
    -------
    list[MaterialTemplate]
        All matching templates (may be empty).
    """
    if cbr < 0:
        raise ValueError(f"CBR must be >= 0, got {cbr}")
    result: list[MaterialTemplate] = []
    for tmpl in MATERIAL_CATALOG:
        lo, hi = tmpl.cbr_range
        if lo <= cbr and (hi is None or cbr < hi):
            result.append(tmpl)
    return result


def find_by_class(g_class: str) -> MaterialTemplate | None:
    """Return the TRH 14 template for a given G-class.

    Parameters
    ----------
    g_class:
        TRH 14 material class, e.g. ``"G5"``.

    Returns
    -------
    MaterialTemplate | None
        The matching template, or ``None`` if not found.
    """
    for tmpl in MATERIAL_CATALOG:
        if tmpl.material_class == g_class:
            return tmpl
    return None


def list_all() -> list[MaterialTemplate]:
    """Return all templates in the catalog."""
    return list(MATERIAL_CATALOG)
