"""Sensitivity analysis for pavement design parameters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

__all__ = ["SensitivityResult", "analyze_sensitivity"]


@dataclass(frozen=True)
class SensitivityResult:
    variable: str
    baseline: float
    perturbations: list[tuple[float, float]]
    confidence: Literal["high", "medium", "low"] = "medium"


def analyze_sensitivity(
    traffic: object,
    subgrade_cbr: float,
    *,
    variable: Literal["cbr", "coverages", "design_life"],
    range_pct: float = 20.0,
    curve_id: str = "usace_cbr_v1",
) -> SensitivityResult:
    if range_pct <= 0:
        raise ValueError(f"range_pct must be > 0, got {range_pct}")

    from haulpave.models.traffic import TrafficInput
    from haulpave.pavement import design_pavement
    from haulpave.utils.interpolation import interpolate_thickness, load_curve_data

    if not isinstance(traffic, TrafficInput):
        raise TypeError(f"traffic must be a TrafficInput, got {type(traffic)}")

    base_result = design_pavement(traffic, subgrade_cbr, curve_id)
    curve_data = load_curve_data(curve_id)

    if variable == "cbr":
        baseline_val = subgrade_cbr
        base_cov = base_result.total_coverages
        base_thickness = base_result.required_thickness_mm
        cbr_min = float(curve_data["cbr_values"][0])
        cbr_max = float(curve_data["cbr_values"][-1])

        perturbations: list[tuple[float, float]] = []
        for pct in [-range_pct, -range_pct / 2, 0, range_pct / 2, range_pct]:
            perturbed = baseline_val * (1 + pct / 100)
            clamped = max(cbr_min, min(cbr_max, perturbed))
            thickness, _ = interpolate_thickness(curve_data, cbr=clamped, coverages=base_cov)
            perturbations.append((clamped, thickness))

        return SensitivityResult(
            variable="cbr",
            baseline=baseline_val,
            perturbations=perturbations,
        )

    elif variable == "coverages":
        baseline_val = base_result.total_coverages
        base_cbr = subgrade_cbr
        base_thickness = base_result.required_thickness_mm

        perturbations = []
        for pct in [-range_pct, -range_pct / 2, 0, range_pct / 2, range_pct]:
            perturbed = baseline_val * (1 + pct / 100)
            if perturbed <= 0:
                perturbed = 1.0
            thickness, _ = interpolate_thickness(curve_data, cbr=base_cbr, coverages=perturbed)
            perturbations.append((perturbed, thickness))

        return SensitivityResult(
            variable="coverages",
            baseline=baseline_val,
            perturbations=perturbations,
        )

    elif variable == "design_life":
        baseline_val = traffic.design_life_years
        base_thickness = base_result.required_thickness_mm
        base_cbr = subgrade_cbr

        perturbations = []
        for pct in [-range_pct, -range_pct / 2, 0, range_pct / 2, range_pct]:
            perturbed_life = baseline_val * (1 + pct / 100)
            if perturbed_life <= 0:
                perturbed_life = 0.5
            modified = traffic.model_copy(update={"design_life_years": perturbed_life})
            mod_result = design_pavement(modified, base_cbr, curve_id)
            perturbations.append((perturbed_life, mod_result.required_thickness_mm))

        return SensitivityResult(
            variable="design_life",
            baseline=baseline_val,
            perturbations=perturbations,
        )

    raise ValueError(f"Unknown variable: {variable}")
