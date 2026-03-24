# HaulPave — Scope Boundary

This document defines what HaulPave does and does not do. It exists to prevent
scope creep and to be honest with users about the tool's limitations.

## In Scope (v0.1 → v1.0)

| Domain | What's Included |
|--------|----------------|
| Traffic loading | Fleet composition → CESA and design coverages (AASHTO-based) |
| Pavement structure | Layer thickness design via CBR-based method (USACE) |
| Material properties | CBR, elastic modulus, basic classification |
| Vehicle database | Specifications for common haul trucks and support vehicles |
| Operating cost analysis | Scenario-based cost comparison with explicit assumptions |
| Reporting | Structured summaries in code, Excel export (v0.3) |

## Explicitly Out of Scope

| Domain | Why |
|--------|-----|
| Geometric design | Different discipline; requires alignment/profile software |
| Drainage design | Requires hydrology |
| Berm / safety bund design | Mine safety regulations |
| Intersection / ramp design | Geometric + traffic ops |
| Grade / gradient optimisation | Requires pit design integration |
| Ride quality (IRI/roughness) | Requires time-series monitoring data |
| Maintenance scheduling | Operations domain |
| Traffic simulation | Different tool category |
| FEM / advanced numerical | Deferred to post-v1.0 |

## Scope Evolution Policy

New features are only added when:

1. They have a clear published engineering method backing them.
2. At least one benchmark case exists to test against.
3. They don't compromise the reliability of existing modules.
4. A maintainer commits to owning the validation.
