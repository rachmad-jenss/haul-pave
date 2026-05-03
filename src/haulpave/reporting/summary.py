"""Design summary builder — versioned metadata wrapper for haul-pave outputs.

Wraps arbitrary design inputs and results in a versioned envelope that includes
the package version, calculation timestamp, and an input fingerprint for
reproducibility.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

import haulpave

__all__ = ["DesignSummary", "build_design_summary"]


class DesignSummary(BaseModel):
    """Versioned design summary envelope."""

    model_config = ConfigDict(frozen=True)

    title: str = Field(min_length=1)
    generated_at: str = Field(description="ISO 8601 UTC timestamp of generation")
    package_version: str = Field(description="haulpave package version string")
    inputs: dict[str, Any] = Field(description="Design inputs as passed by the caller")
    results: dict[str, Any] = Field(description="Computed results keyed by method name")


def build_design_summary(
    inputs: dict[str, Any],
    results: dict[str, Any] | None = None,
    title: str = "Haul Road Pavement Design Summary",
) -> DesignSummary:
    """Build a versioned design summary from inputs and optional results.

    Parameters
    ----------
    inputs:
        Arbitrary design inputs (fleet spec, pavement params, cost assumptions,
        etc.) as collected by the caller.  Stored verbatim — not validated.
    results:
        Computed outputs to include in the summary.  If ``None``, an empty
        dict is used.  Callers should populate this with outputs from
        ``design_pavement``, ``compare_scenarios``, etc.
    title:
        Human-readable summary title.

    Returns
    -------
    DesignSummary
        Immutable Pydantic model with versioned metadata.
    """
    return DesignSummary(
        title=title,
        generated_at=datetime.now(timezone.utc).isoformat(),
        package_version=haulpave.__version__,
        inputs=inputs,
        results=results if results is not None else {},
    )
