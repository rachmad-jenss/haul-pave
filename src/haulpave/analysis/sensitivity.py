"""Sensitivity analysis for pavement design parameters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from haulpave.pavement import design_pavement
from haulpave.utils.interpolation import interpolate_thickness, load_curve_data

if TYPE_CHECKING:
    from haulpave.models.traffic import TrafficInput

__all__ = ["SensitivityResult", "analyze_sensitivity"]


@dataclass(frozen=True)
class SensitivityResult:
    """Result of a pavement design sensitivity analysis.

    Attributes
    ----------
    variable:
        Name of the design parameter that was perturbed (``"cbr"``,
        ``"coverages"``, or ``"design_life"``).
    baseline:
        Original value of the variable before perturbation.
    perturbations:
        List of ``(perturbed_value, resulting_thickness_mm)`` pairs for
        each perturbation point.  Always includes the baseline point.
    confidence:
        Confidence label following the project plan convention.
    """

    variable: str
    baseline: float
    perturbations: list[tuple[float, float]]
    confidence: Literal["high", "medium", "low"] = "medium"


def analyze_sensitivity(
    traffic: TrafficInput,
    subgrade_cbr: float,
    *,
    variable: Literal["cbr", "coverages", "design_life"],
    range_pct: float = 20.0,
    curve_id: str = "usace_cbr_v1",
) -> SensitivityResult:
    """Analyse how pavement thickness responds to changes in a design parameter.

    Perturbs *variable* by ``±range_pct`` and ``±range_pct/2`` (5 points)
    and interpolates the required pavement thickness at each perturbed
    value.  Perturbed values that fall outside the curve's supported range
    are clamped to the nearest boundary.

    Parameters
    ----------
    traffic:
        ``TrafficInput`` describing the fleet mix and design life.
    subgrade_cbr:
        Subgrade CBR [%].  Must be within the curve's supported range.
    variable:
        Which parameter to perturb — ``"cbr"``, ``"coverages"``, or
        ``"design_life"``.
    range_pct:
        Half-range of the perturbation as a percentage of the baseline
        (default 20 %).  Must be > 0.
    curve_id:
        Digitised curve dataset identifier (default ``"usace_cbr_v1"``).

    Returns
    -------
    SensitivityResult
        Frozen dataclass with the perturbation table.

    Raises
    ------
    ValueError
        If *range_pct* ≤ 0 or *variable* is not recognised.
    TypeError
        If *traffic* is not a ``TrafficInput`` instance.
    """
    if range_pct <= 0:
        raise ValueError(f"range_pct must be > 0, got {range_pct}")

    base_result = design_pavement(traffic, subgrade_cbr, curve_id)
    curve_data = load_curve_data(curve_id)

    if variable == "cbr":
        baseline_val = subgrade_cbr
        base_cov = base_result.total_coverages
        cbr_min = float(curve_data["cbr_values"][0])
        cbr_max = float(curve_data["cbr_values"][-1])

        perturbations: list[tuple[float, float]] = []
        for pct in [-range_pct, -range_pct / 2, 0, range_pct / 2, range_pct]:
            perturbed = baseline_val * (1 + pct / 100)
            clamped = max(cbr_min, min(cbr_max, perturbed))
            thickness, _was_clamped, _was_extrapolated = interpolate_thickness(
                curve_data, cbr=clamped, coverages=base_cov
            )
            perturbations.append((clamped, thickness))

        return SensitivityResult(variable="cbr", baseline=baseline_val, perturbations=perturbations)

    elif variable == "coverages":
        baseline_val = base_result.total_coverages
        cov_levels = curve_data["coverage_levels"]
        cov_min = float(cov_levels[0])
        cov_max = float(cov_levels[-1])

        perturbations = []
        for pct in [-range_pct, -range_pct / 2, 0, range_pct / 2, range_pct]:
            perturbed = baseline_val * (1 + pct / 100)
            clamped = max(cov_min, min(cov_max, perturbed))
            thickness, _was_clamped, _was_extrapolated = interpolate_thickness(
                curve_data, cbr=subgrade_cbr, coverages=clamped
            )
            perturbations.append((clamped, thickness))

        return SensitivityResult(
            variable="coverages", baseline=baseline_val, perturbations=perturbations
        )

    elif variable == "design_life":
        baseline_val = traffic.design_life_years
        min_life = 0.25

        perturbations = []
        for pct in [-range_pct, -range_pct / 2, 0, range_pct / 2, range_pct]:
            perturbed_life = baseline_val * (1 + pct / 100)
            clamped_life = max(min_life, perturbed_life)
            modified = traffic.model_copy(update={"design_life_years": clamped_life})
            mod_result = design_pavement(modified, subgrade_cbr, curve_id)
            perturbations.append((clamped_life, mod_result.required_thickness_mm))

        return SensitivityResult(
            variable="design_life", baseline=baseline_val, perturbations=perturbations
        )

    raise ValueError(f"Unknown variable: {variable!r}")
