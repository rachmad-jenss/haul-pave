"""PCHIP interpolation utilities for HaulPave empirical curve data."""

from __future__ import annotations

import json
import warnings
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


def _validate_curve_data(curve_data: dict[str, Any]) -> None:
    """Validate curve data structure before interpolation.

    Args:
        curve_data: Loaded curve JSON.

    Raises:
        ValueError: If curve data is malformed or inconsistent.
    """
    required_keys = {"cbr_values", "coverage_levels", "thickness_mm"}
    missing = required_keys - curve_data.keys()
    if missing:
        raise ValueError(f"curve_data missing required keys: {missing}")

    cbr_values = curve_data["cbr_values"]
    coverage_levels = curve_data["coverage_levels"]
    thickness_mm = curve_data["thickness_mm"]

    if len(cbr_values) < 2:
        raise ValueError("cbr_values must have at least 2 points")
    if len(coverage_levels) < 2:
        raise ValueError("coverage_levels must have at least 2 points")

    n_cbr = len(cbr_values)
    for cov_key in coverage_levels:
        key = str(cov_key)
        if key not in thickness_mm:
            raise ValueError(f"thickness_mm missing coverage level key '{key}'")
        if len(thickness_mm[key]) != n_cbr:
            raise ValueError(
                f"thickness_mm['{key}'] has {len(thickness_mm[key])} values, "
                f"expected {n_cbr} (len of cbr_values)"
            )


def _get_extrapolated_levels(curve_data: dict[str, Any]) -> set[float]:
    """Return the set of extrapolated coverage levels from the curve data."""
    raw = curve_data.get("extrapolated_coverage_levels", [])
    return {float(v) for v in raw}


def interpolate_thickness(
    curve_data: dict[str, Any],
    cbr: float,
    coverages: float,
) -> tuple[float, bool, bool]:
    """Interpolate required pavement thickness for given CBR and design coverages.

    Uses 2-step PCHIP interpolation:
    1. Interpolate thickness vs CBR at each coverage level.
    2. Log-linear interpolation between coverage levels.

    Out-of-range coverages (positive) are clamped to the curve boundary.
    Out-of-range CBR raises ValueError.

    Args:
        curve_data: Loaded curve JSON (from load_curve_data).
        cbr: Subgrade CBR [%], must be within curve range.
        coverages: Design coverages (number), must be > 0. Values outside
            the curve's coverage range are clamped to the boundary.

    Returns:
        Tuple of (required total pavement thickness [mm], was_clamped,
        was_extrapolated). ``was_extrapolated`` is True when coverages are
        within the extended range but lie beyond the original (digitized)
        curve data — i.e. the result is an extrapolation.

    Raises:
        ValueError: If CBR is outside the supported range, coverages <= 0,
            or curve_data is malformed.
    """
    _validate_curve_data(curve_data)

    cbr_values = np.array(curve_data["cbr_values"], dtype=float)
    coverage_levels = np.array(curve_data["coverage_levels"], dtype=float)

    if cbr < cbr_values[0] or cbr > cbr_values[-1]:
        raise ValueError(f"CBR {cbr} outside supported range [{cbr_values[0]}, {cbr_values[-1]}]")
    if coverages <= 0:
        raise ValueError(f"coverages must be > 0, got {coverages}")

    # Determine the digitized (original) coverage max
    extrapolated_set = _get_extrapolated_levels(curve_data)
    if extrapolated_set:
        digitized_levels = [v for v in coverage_levels if v not in extrapolated_set]
    else:
        digitized_levels = list(coverage_levels)
    digitized_max = max(digitized_levels) if digitized_levels else coverage_levels[-1]

    was_clamped = False
    was_extrapolated = False
    if coverages < coverage_levels[0]:
        warnings.warn(
            f"USACE CBR: design coverages ({coverages:.0f}) below curve minimum "
            f"({coverage_levels[0]:.0f}), clamped to {coverage_levels[0]:.0f}.",
            UserWarning,
            stacklevel=2,
        )
        was_clamped = True
    elif coverages > coverage_levels[-1]:
        warnings.warn(
            f"USACE CBR: design coverages ({coverages:.0f}) exceed curve maximum "
            f"({coverage_levels[-1]:.0f}), clamped to {coverage_levels[-1]:.0f}.",
            UserWarning,
            stacklevel=2,
        )
        was_clamped = True
    elif coverages > digitized_max:
        was_extrapolated = True

    cov_clamped = float(np.clip(coverages, coverage_levels[0], coverage_levels[-1]))
    log_cov = np.log10(cov_clamped)
    log_cov_levels = np.log10(coverage_levels)

    # For each coverage level, interpolate thickness at the requested CBR
    thicknesses_at_coverages: list[float] = []
    for cov_key in curve_data["coverage_levels"]:
        t_arr = np.array(curve_data["thickness_mm"][str(cov_key)], dtype=float)
        pchip = PchipInterpolator(cbr_values, t_arr)
        thicknesses_at_coverages.append(float(pchip(cbr)))

    # Interpolate across coverage levels (log scale)
    cov_pchip = PchipInterpolator(log_cov_levels, thicknesses_at_coverages)
    return float(cov_pchip(log_cov)), was_clamped, was_extrapolated
