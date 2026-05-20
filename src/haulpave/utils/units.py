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
    "psi_to_kpa",
    "kpa_to_psi",
    "tons_to_tonnes",
    "tonnes_to_tons",
    "lbs_to_kg",
    "inches_to_mm",
    "mm_to_inches",
    "feet_to_m",
    "sq_inches_to_cm2",
    "sq_feet_to_m2",
    "lbf_to_kn",
    "kn_to_lbf",
    "mph_to_kmh",
    "kmh_to_mph",
]

# ---- Pressure ----------------------------------------------------------


def psi_to_kpa(psi: float) -> float:
    return psi * 6.89476


def kpa_to_psi(kpa: float) -> float:
    return kpa / 6.89476


# ---- Mass --------------------------------------------------------------


def tons_to_tonnes(short_tons: float) -> float:
    return short_tons * 0.907185


def tonnes_to_tons(tonnes: float) -> float:
    return tonnes / 0.907185


def lbs_to_kg(lbs: float) -> float:
    return lbs * 0.453592


# ---- Length ------------------------------------------------------------


def inches_to_mm(inches: float) -> float:
    return inches * 25.4


def mm_to_inches(mm: float) -> float:
    return mm / 25.4


def feet_to_m(feet: float) -> float:
    return feet * 0.3048


# ---- Area --------------------------------------------------------------


def sq_inches_to_cm2(sq_in: float) -> float:
    return sq_in * 6.4516


def sq_feet_to_m2(sq_ft: float) -> float:
    return sq_ft * 0.092903


# ---- Force -------------------------------------------------------------


def lbf_to_kn(lbf: float) -> float:
    return lbf * 0.00444822


def kn_to_lbf(kn: float) -> float:
    return kn / 0.00444822


# ---- Speed -------------------------------------------------------------


def mph_to_kmh(mph: float) -> float:
    return mph * 1.60934


def kmh_to_mph(kmh: float) -> float:
    return kmh / 1.60934
