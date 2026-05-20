"""Unit tests for haulpave.reporting.summary."""

from __future__ import annotations

import pytest

from haulpave.reporting.summary import DesignSummary, build_design_summary


class TestBuildDesignSummary:
    def test_returns_design_summary(self) -> None:
        result = build_design_summary(inputs={"cbr": 10})
        assert isinstance(result, DesignSummary)

    def test_fields_present(self) -> None:
        result = build_design_summary(
            inputs={"cbr": 10, "coverages": 1000},
            results={"trh14": {"thickness_mm": 428.7}},
            title="Test Summary",
        )
        assert result.title == "Test Summary"
        assert result.inputs["cbr"] == 10
        assert result.results["trh14"]["thickness_mm"] == 428.7
        assert "package_version" in result.model_fields_set
        assert "generated_at" in result.model_fields_set

    def test_none_results_defaults_to_empty(self) -> None:
        result = build_design_summary(inputs={"cbr": 5})
        assert result.results == {}

    def test_immutable(self) -> None:
        result = build_design_summary(inputs={"cbr": 10})
        with pytest.raises(Exception):
            result.title = "Changed"  # type: ignore[misc]
