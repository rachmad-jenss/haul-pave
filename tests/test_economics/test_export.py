"""Unit tests for economics.export — Excel export."""

from __future__ import annotations

from pathlib import Path

import pytest

openpyxl = pytest.importorskip("openpyxl", reason="openpyxl is required for Excel export tests")

from haulpave.economics.compare import (  # noqa: E402
    ComparisonResult,
    RoadScenario,
    compare_scenarios,
)
from haulpave.economics.export import export_comparison_to_excel  # noqa: E402


@pytest.fixture()
def comparison_result() -> ComparisonResult:
    scenarios = [
        RoadScenario(
            name="Asphalt",
            surface="asphalt",
            haul_distance_km=5.0,
            trips_per_day=20,
        ),
        RoadScenario(
            name="Gravel",
            surface="gravel",
            haul_distance_km=5.0,
            trips_per_day=20,
        ),
        RoadScenario(
            name="Concrete",
            surface="concrete",
            haul_distance_km=5.0,
            trips_per_day=20,
        ),
    ]
    return compare_scenarios(scenarios)


class TestExportComparisonToExcel:
    def test_export_creates_valid_xlsx(
        self,
        comparison_result: ComparisonResult,
        tmp_path: Path,
    ) -> None:
        filepath = tmp_path / "comparison.xlsx"
        result = export_comparison_to_excel(comparison_result, filepath)
        assert Path(result).exists()
        assert Path(result).suffix == ".xlsx"

    def test_export_file_can_be_opened(
        self,
        comparison_result: ComparisonResult,
        tmp_path: Path,
    ) -> None:
        filepath = tmp_path / "comparison.xlsx"
        export_comparison_to_excel(comparison_result, filepath)
        wb = openpyxl.load_workbook(filepath)
        assert "Scenario Comparison" in wb.sheetnames
        ws = wb["Scenario Comparison"]
        assert ws is not None
        wb.close()

    def test_all_scenarios_present(
        self,
        comparison_result: ComparisonResult,
        tmp_path: Path,
    ) -> None:
        filepath = tmp_path / "comparison.xlsx"
        export_comparison_to_excel(comparison_result, filepath)
        wb = openpyxl.load_workbook(filepath)
        ws = wb["Scenario Comparison"]
        n = len(comparison_result.scenarios)
        names = [ws.cell(row=r, column=1).value for r in range(6, 6 + n)]
        assert "Asphalt" in names
        assert "Gravel" in names
        assert "Concrete" in names
        wb.close()

    def test_export_returns_absolute_path(
        self,
        comparison_result: ComparisonResult,
        tmp_path: Path,
    ) -> None:
        filepath = tmp_path / "comparison.xlsx"
        result = export_comparison_to_excel(comparison_result, filepath)
        assert result == str(Path(filepath).resolve())

    def test_metadata_present(
        self,
        comparison_result: ComparisonResult,
        tmp_path: Path,
    ) -> None:
        filepath = tmp_path / "comparison.xlsx"
        export_comparison_to_excel(comparison_result, filepath)
        wb = openpyxl.load_workbook(filepath)
        ws = wb["Scenario Comparison"]
        assert ws["B1"].value == comparison_result.method
        assert ws["B2"].value == comparison_result.confidence
        assert ws["B3"].value is not None
        wb.close()
