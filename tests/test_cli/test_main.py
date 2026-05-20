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


_SCENARIO_DATA = {
    "scenario_id": "test_haul",
    "haul_distance_km": 5.0,
    "average_speed_kmh": 35.0,
    "payload_t": 150.0,
    "fuel_consumption_l_per_km": 2.5,
    "assumptions": {
        "fuel_cost_per_litre": 0.80,
        "tyre_cost_per_hour": 45.0,
        "maintenance_cost_per_km": 0.35,
        "operator_cost_per_hour": 38.0,
        "currency": "USD",
    },
}

_ROADS_DATA = [
    {
        "name": "Gravel",
        "surface": "gravel",
        "thickness_mm": 500.0,
        "haul_distance_km": 5.0,
        "trips_per_day": 40.0,
    },
    {
        "name": "Asphalt",
        "surface": "asphalt",
        "thickness_mm": 450.0,
        "haul_distance_km": 5.0,
        "trips_per_day": 40.0,
    },
]


@pytest.fixture()
def scenario_json(tmp_path: Path) -> Path:
    p = tmp_path / "scenario.json"
    p.write_text(json.dumps(_SCENARIO_DATA))
    return p


@pytest.fixture()
def roads_json(tmp_path: Path) -> Path:
    p = tmp_path / "roads.json"
    p.write_text(json.dumps(_ROADS_DATA))
    return p


class TestEconomics:
    def test_economics_text(self, scenario_json: Path) -> None:
        result = runner.invoke(
            app, ["economics", "-i", str(scenario_json), "--trips-per-day", "40"]
        )
        assert result.exit_code == 0
        assert "Cost per trip" in result.output
        assert "Annual cost" in result.output

    def test_economics_json(self, scenario_json: Path) -> None:
        result = runner.invoke(
            app,
            ["economics", "-i", str(scenario_json), "--trips-per-day", "40", "--json"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "cost_per_trip" in data
        assert data["cost_per_trip"] > 0

    def test_economics_zero_trips(self, scenario_json: Path) -> None:
        result = runner.invoke(app, ["economics", "-i", str(scenario_json)])
        assert result.exit_code == 0
        assert "Annual cost" in result.output

    def test_economics_missing_file(self) -> None:
        result = runner.invoke(app, ["economics", "-i", "nonexistent.json"])
        assert result.exit_code == 1
        assert isinstance(result.exception, FileNotFoundError)


class TestScenario:
    def test_scenario_text(self, roads_json: Path) -> None:
        result = runner.invoke(app, ["scenario", "-i", str(roads_json)])
        assert result.exit_code == 0
        assert "Gravel" in result.output
        assert "Asphalt" in result.output

    def test_scenario_json(self, roads_json: Path) -> None:
        result = runner.invoke(app, ["scenario", "-i", str(roads_json), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "scenarios" in data
        assert len(data["scenarios"]) == 2

    def test_scenario_fuel_price(self, roads_json: Path) -> None:
        result = runner.invoke(
            app, ["scenario", "-i", str(roads_json), "--fuel-price", "1.50", "--json"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        for s in data["scenarios"]:
            assert s["fuel_cost_usd_per_year"] > s["maintenance_cost_usd_per_year"]

    def test_scenario_invalid_json(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("not json")
        result = runner.invoke(app, ["scenario", "-i", str(bad)])
        assert result.exit_code == 1


class TestExport:
    def test_export_creates_file(self, roads_json: Path, tmp_path: Path) -> None:
        pytest.importorskip("openpyxl")
        out = tmp_path / "results.xlsx"
        result = runner.invoke(
            app, ["export", "-i", str(roads_json), "-o", str(out)]
        )
        assert result.exit_code == 0
        assert out.exists()
        assert "Exported" in result.output

    def test_export_missing_input(self, tmp_path: Path) -> None:
        out = tmp_path / "r.xlsx"
        result = runner.invoke(
            app, ["export", "-i", "nope.json", "-o", str(out)]
        )
        assert result.exit_code == 1
