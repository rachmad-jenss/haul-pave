# Benchmark Reference Sources

Full bibliographic citations for all sources used in benchmark expected values.
Each entry notes which benchmark(s) it applies to and which equations or figures are used.

---

## AASHTO (Bench 01 — CESA)

- **Citation**: American Association of State Highway and Transportation Officials (AASHTO). (1993). *AASHTO Guide for Design of Pavement Structures, 4th Edition*. Washington, D.C.: AASHTO.
- **Equation used**: Equivalent Single Axle Load (ESAL) 4th power law, Section 2.
- **Standard axle**: 80 kN single axle, 160 kN tandem axle group.
- **Notes**: The 4th power law (load equivalency factor = (axle load / standard axle load)^4) is the canonical ESAL formula used throughout North American pavement design practice. Single-axle standard = 80 kN; tandem-axle standard = 160 kN.

---

## USACE TM 5-822-12 (Bench 02 — Coverages, Bench 03 — CBR Thickness)

- **Citation**: U.S. Army Corps of Engineers. (1987). *Technical Manual TM 5-822-12: Flexible Pavement Design for Airfields (Unified Facilities Criteria)*. Washington, D.C.: USACE.
- **Used for**:
  - Design coverages definition and pass-count method (Section 3-2) → Bench 02
  - CBR design curves (Figure 1) → Bench 03
- **Notes**: Document is in the public domain (U.S. Government publication). Available from the Defense Technical Information Center (DTIC). The coverage concept from TM 5-822-12 has been adapted for mine haul road design practice; the adaptation is documented in the engine source.

---

## Vehicle Specifications

The following OEM spec sheets are the authoritative source for all vehicle parameters (axle loads, GVM, tyre contact pressures) used in the benchmark fleet fixtures defined in `tests/conftest.py`.

- Caterpillar Inc. (2023). *Cat 793F Mining Truck Specifications*. Peoria, IL: Caterpillar. [AEHQ6998-02 or current rev.]
- Caterpillar Inc. (2023). *Cat 785D Mining Truck Specifications*. Peoria, IL: Caterpillar. [AEHQ5711 or current rev.]
- Caterpillar Inc. (2023). *Cat 777G Mining Truck Specifications*. Peoria, IL: Caterpillar. [AEHQ6572 or current rev.]

**Note on ancillary equipment**: Fuel truck, motor grader, and water truck specs in `tests/conftest.py` are labelled `"Generic … spec"` and use representative industry values. These are for benchmark sensitivity purposes only; they are not intended for site-specific design without independent verification.

---

## Bench 04 Source (Pending)

A published mine haul road operating cost case study will be identified during DAS-102 development and cited here before Bench 04 is written. The citation must include:

- Author(s), year, title, publication/journal/conference
- Specific cost breakdown figures used as expected values
- Currency year and normalisation basis (cost per tonne-km or similar)
