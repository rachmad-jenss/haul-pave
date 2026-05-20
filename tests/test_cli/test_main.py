"""Tests for haulpave CLI commands."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from haulpave.cli.main import app

runner = CliRunner()


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


# Minimal traffic JSON for CLI tests
_TRAFFIC_DATA = {
    "fleet": [
        {
            "vehicle": {
                "name": "Test Truck",
                "gross_vehicle_mass_t": 100.0,
                "axle_groups": [
                    {
                        "axle_count": 1,
                        "tyres_per_axle": 2,
                        "gross_load_kn": 200.0,
                        "tire_spec": {
                            "contact_pressure_kpa": 700.0,
                            "contact_area_mm2": 5000.0,
                        },
                    }
                ],
                "source": "CLI test fixture",
            },
            "trips_per_day": 10,
        }
    ],
    "design_life_years": 5,
    "working_days_per_year": 300,
}


@pytest.fixture()
def traffic_json(tmp_path: Path) -> Path:
    """Write traffic data to a temp JSON file."""
    p = tmp_path / "traffic.json"
    p.write_text(json.dumps(_TRAFFIC_DATA))
    return p


class TestVersion:
    def test_version_output(self) -> None:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "HaulPave" in result.output


class TestCesa:
    def test_cesa_text(self, traffic_json: Path) -> None:
        result = runner.invoke(app, ["cesa", "-i", str(traffic_json)])
        assert result.exit_code == 0
        assert "Total CESA" in result.output
        assert "AASHTO" in result.output

    def test_cesa_json(self, traffic_json: Path) -> None:
        result = runner.invoke(app, ["cesa", "-i", str(traffic_json), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "total_cesa" in data
        assert data["total_cesa"] > 0


class TestCoverages:
    def test_coverages_text(self, traffic_json: Path) -> None:
        result = runner.invoke(app, ["coverages", "-i", str(traffic_json)])
        assert result.exit_code == 0
        assert "Total coverages" in result.output
        assert "Design wheel load" in result.output

    def test_coverages_json(self, traffic_json: Path) -> None:
        result = runner.invoke(app, ["coverages", "-i", str(traffic_json), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "total_coverages" in data


class TestDesign:
    def test_design_text(self, traffic_json: Path) -> None:
        result = runner.invoke(app, ["design", "-i", str(traffic_json), "--cbr", "10"])
        assert result.exit_code == 0
        assert "Required thickness" in result.output
        assert "mm" in result.output

    def test_design_json(self, traffic_json: Path) -> None:
        result = runner.invoke(app, ["design", "-i", str(traffic_json), "--cbr", "10", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "required_thickness_mm" in data
        assert data["required_thickness_mm"] > 0

    def test_missing_input_file(self) -> None:
        result = runner.invoke(app, ["design", "-i", "nonexistent.json", "--cbr", "10"])
        assert result.exit_code == 1
        assert isinstance(result.exception, FileNotFoundError)

    def test_invalid_json_input(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("{invalid json}")
        result = runner.invoke(app, ["design", "-i", str(bad), "--cbr", "10"])
        assert result.exit_code == 1
        assert isinstance(result.exception, json.JSONDecodeError)

    def test_invalid_cbr_value(self, traffic_json: Path) -> None:
        result = runner.invoke(app, ["design", "-i", str(traffic_json), "--cbr", "0.5"])
        assert result.exit_code == 1
        assert isinstance(result.exception, ValueError)
        assert "CBR" in str(result.exception)


class TestCompare:
    def test_compare_text(self, traffic_json: Path) -> None:
        result = runner.invoke(app, ["compare", "-i", str(traffic_json), "--cbr", "10"])
        assert result.exit_code == 0
        assert "USACE" in result.output
        assert "TRH 14" in result.output
        assert "Delta" in result.output

    def test_compare_json(self, traffic_json: Path) -> None:
        result = runner.invoke(app, ["compare", "-i", str(traffic_json), "--cbr", "10", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "delta_mm" in data


class TestMissingArgs:
    def test_design_missing_required(self) -> None:
        result = runner.invoke(app, ["design"])
        assert result.exit_code == 2
        assert (
            "Error" in result.output
            or "option" in result.output.lower()
            or "required" in result.output.lower()
        )

    def test_cesa_missing_input(self) -> None:
        result = runner.invoke(app, ["cesa"])
        assert result.exit_code == 2


class TestCliHelp:
    def test_main_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "haulpave" in result.output.lower() or "pavement" in result.output.lower()

    def test_design_help(self) -> None:
        result = runner.invoke(app, ["design", "--help"])
        assert result.exit_code == 0
        output = _strip_ansi(result.output)
        assert "--cbr" in output
        assert "--input" in output
