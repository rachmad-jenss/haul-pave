"""Explicit unit conversion helpers for imperial ↔ SI.

SI units are the internal standard for all HaulPave calculations.
These helpers provide explicit conversion for users sourcing data
in imperial units.  Implicit conversion is never performed —
callers must always convert explicitly before passing data to
HaulPave engine functions.

Conversions follow standard factors from NIST SP 811 and ISO 80000.
"""

from __future__ import annotations

__all__ = [
    "cm2_to_sq_inches",
    "feet_to_m",
    "inches_to_mm",
    "kg_to_lbs",
    "kmh_to_mph",
    "kn_to_lbf",
    "kpa_to_psi",
    "lbf_to_kn",
    "lbs_to_kg",
    "m_to_feet",
    "m2_to_sq_feet",
    "mm_to_inches",
    "mph_to_kmh",
    "psi_to_kpa",
    "sq_feet_to_m2",
    "sq_inches_to_cm2",
    "tonnes_to_tons",
    "tons_to_tonnes",
]

# ---- Pressure ----------------------------------------------------------


def psi_to_kpa(psi: float) -> float:
    """Convert pressure from psi to kPa."""
    return psi * 6.894757293168


def kpa_to_psi(kpa: float) -> float:
    """Convert pressure from kPa to psi."""
    return kpa / 6.894757293168


# ---- Mass --------------------------------------------------------------


def tons_to_tonnes(short_tons: float) -> float:
    """Convert mass from short tons (US) to tonnes."""
    return short_tons * 0.90718474


def tonnes_to_tons(tonnes: float) -> float:
    """Convert mass from tonnes to short tons (US)."""
    return tonnes / 0.90718474


def lbs_to_kg(lbs: float) -> float:
    """Convert mass from pounds to kilograms."""
    return lbs * 0.45359237


def kg_to_lbs(kg: float) -> float:
    """Convert mass from kilograms to pounds."""
    return kg / 0.45359237


# ---- Length ------------------------------------------------------------


def inches_to_mm(inches: float) -> float:
    """Convert length from inches to millimetres."""
    return inches * 25.4


def mm_to_inches(mm: float) -> float:
    """Convert length from millimetres to inches."""
    return mm / 25.4


def feet_to_m(feet: float) -> float:
    """Convert length from feet to metres."""
    return feet * 0.3048


def m_to_feet(m: float) -> float:
    """Convert length from metres to feet."""
    return m / 0.3048


# ---- Area --------------------------------------------------------------


def sq_inches_to_cm2(sq_in: float) -> float:
    """Convert area from square inches to square centimetres."""
    return sq_in * 6.4516


def cm2_to_sq_inches(cm2: float) -> float:
    """Convert area from square centimetres to square inches."""
    return cm2 / 6.4516


def sq_feet_to_m2(sq_ft: float) -> float:
    """Convert area from square feet to square metres."""
    return sq_ft * 0.09290304


def m2_to_sq_feet(m2: float) -> float:
    """Convert area from square metres to square feet."""
    return m2 / 0.09290304


# ---- Force -------------------------------------------------------------


def lbf_to_kn(lbf: float) -> float:
    """Convert force from pound-force to kilonewtons."""
    return lbf * 0.0044482216152605


def kn_to_lbf(kn: float) -> float:
    """Convert force from kilonewtons to pound-force."""
    return kn / 0.0044482216152605


# ---- Speed -------------------------------------------------------------


def mph_to_kmh(mph: float) -> float:
    """Convert speed from miles per hour to kilometres per hour."""
    return mph * 1.609344


def kmh_to_mph(kmh: float) -> float:
    """Convert speed from kilometres per hour to miles per hour."""
    return kmh / 1.609344
