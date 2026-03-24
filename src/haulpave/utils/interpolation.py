"""PCHIP interpolation utilities for HaulPave empirical curve data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.interpolate import PchipInterpolator

CURVES_DIR = Path(__file__).parent.parent / "design" / "curves"


def load_curve_data(curve_id: str) -> dict[str, Any]:
    """Load digitized curve JSON by curve_id."""
    path = CURVES_DIR / f"{curve_id}.json"
    with path.open() as f:
        return json.load(f)  # type: ignore[no-any-return]


def interpolate_thickness(
    curve_data: dict[str, Any],
    cbr: float,
    coverages: float,
) -> float:
    """Interpolate required pavement thickness for given CBR and design coverages.

    Uses 2-step PCHIP interpolation:
    1. Interpolate thickness vs CBR at the two bounding coverage levels.
    2. Log-linear interpolation between coverage levels.

    Args:
        curve_data: Loaded curve JSON (from load_curve_data).
        cbr: Subgrade CBR [%], must be within curve range.
        coverages: Design coverages (number), must be > 0.

    Returns:
        Required total pavement thickness [mm].

    Raises:
        ValueError: If CBR or coverages are outside supported range.
    """
    cbr_values = np.array(curve_data["cbr_values"], dtype=float)
    coverage_levels = np.array(curve_data["coverage_levels"], dtype=float)

    if cbr < cbr_values[0] or cbr > cbr_values[-1]:
        raise ValueError(f"CBR {cbr} outside supported range [{cbr_values[0]}, {cbr_values[-1]}]")
    if coverages <= 0:
        raise ValueError(f"coverages must be > 0, got {coverages}")

    # Clamp coverages to range
    log_cov = np.log10(np.clip(coverages, coverage_levels[0], coverage_levels[-1]))
    log_cov_levels = np.log10(coverage_levels)

    # For each coverage level, interpolate thickness at the requested CBR
    thicknesses_at_coverages: list[float] = []
    for cov_key in curve_data["coverage_levels"]:
        t_arr = np.array(curve_data["thickness_mm"][str(cov_key)], dtype=float)
        pchip = PchipInterpolator(cbr_values, t_arr)
        thicknesses_at_coverages.append(float(pchip(cbr)))

    # Interpolate across coverage levels (log scale)
    cov_pchip = PchipInterpolator(log_cov_levels, thicknesses_at_coverages)
    return float(cov_pchip(log_cov))
