"""Unit tests for haulpave.reporting.summary."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from haulpave.reporting.summary import DesignSummary, build_design_summary, compute_input_hash


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

    def test_input_hash_present(self) -> None:
        result = build_design_summary(inputs={"cbr": 10})
        assert result.input_hash is not None
        assert len(result.input_hash) == 64
        assert all(c in "0123456789abcdef" for c in result.input_hash)

    def test_input_hash_deterministic(self) -> None:
        a = build_design_summary(inputs={"cbr": 10, "coverages": 5000})
        b = build_design_summary(inputs={"cbr": 10, "coverages": 5000})
        assert a.input_hash == b.input_hash

    def test_input_hash_differs_for_different_inputs(self) -> None:
        a = build_design_summary(inputs={"cbr": 10})
        b = build_design_summary(inputs={"cbr": 15})
        assert a.input_hash != b.input_hash

    def test_input_hash_dict_order_agnostic(self) -> None:
        a = build_design_summary(inputs={"cbr": 10, "coverages": 5000})
        b = build_design_summary(inputs={"coverages": 5000, "cbr": 10})
        assert a.input_hash == b.input_hash


class TestComputeInputHash:
    def test_returns_hex_string(self) -> None:
        h = compute_input_hash({"cbr": 10})
        assert isinstance(h, str)
        assert len(h) == 64

    def test_same_inputs_same_hash(self) -> None:
        assert compute_input_hash({"a": 1, "b": 2}) == compute_input_hash({"a": 1, "b": 2})

    def test_different_inputs_different_hash(self) -> None:
        assert compute_input_hash({"a": 1}) != compute_input_hash({"a": 2})

    def test_nested_dicts(self) -> None:
        h = compute_input_hash({"fleet": [{"name": "Test", "trips": 10}]})
        assert len(h) == 64
