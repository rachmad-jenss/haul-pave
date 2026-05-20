"""HaulPave command-line interface.

Commands:
  version    — Print the HaulPave version.
  cesa       — Compute CESA from a traffic JSON file.
  coverages  — Compute design coverages from a traffic JSON file.
  design     — Run USACE CBR pavement design.
  compare    — Run USACE vs TRH 14 comparison.
  economics  — Compute operating cost from a scenario JSON file.
  scenario   — Compare operating costs across road surface types.
  export     — Export scenario comparison to Excel (.xlsx).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer

app = typer.Typer(
    name="haulpave",
    help="Pavement structure and operating-cost analysis for mine haul roads.",
    add_completion=False,
)


def _load_traffic(input_path: Path) -> Any:
    """Load and parse a traffic JSON file, returning validated TrafficInput."""
    from haulpave.models.traffic import TrafficInput

    with input_path.open(encoding="utf-8") as f:
        data: Any = json.load(f)
    return TrafficInput.model_validate(data)


def _print_json(obj: Any) -> None:
    """Print a frozen dataclass result as formatted JSON to stdout."""
    from dataclasses import asdict

    typer.echo(json.dumps(asdict(obj), indent=2))


@app.command()
def version() -> None:
    """Print the HaulPave version."""
    from haulpave import __version__

    typer.echo(f"HaulPave {__version__}")


_InputPath = Annotated[Path, typer.Option("--input", "-i", help="Path to traffic JSON file")]
_JsonFlag = Annotated[bool, typer.Option("--json", help="Output as JSON")]
_CbrOption = Annotated[float, typer.Option("--cbr", help="Subgrade CBR [%]")]
_CurveIdOption = Annotated[str, typer.Option("--curve-id", help="Curve dataset ID")]
_OutputPath = Annotated[Path, typer.Option("--output", "-o", help="Output file path")]
_TripsPerDay = Annotated[float, typer.Option("--trips-per-day", help="One-way trips per day")]
_WorkingDays = Annotated[int, typer.Option("--working-days", help="Working days per year")]
_FuelPrice = Annotated[float, typer.Option("--fuel-price", help="Fuel price [USD/L]")]


@app.command()
def cesa(
    input_path: _InputPath,
    output_json: _JsonFlag = False,
) -> None:
    """Compute Cumulative Equivalent Standard Axles (CESA)."""
    from haulpave.traffic.cesa import compute_cesa

    traffic = _load_traffic(input_path)
    result = compute_cesa(traffic)

    if output_json:
        _print_json(result)
    else:
        typer.echo(f"Method:     {result.method}")
        typer.echo(f"Total CESA: {result.total_cesa:,.0f}")
        typer.echo(f"Confidence: {result.confidence}")


@app.command()
def coverages(
    input_path: _InputPath,
    output_json: _JsonFlag = False,
) -> None:
    """Compute design coverages (USACE TM 5-822-12)."""
    from haulpave.traffic.coverages import compute_coverages

    traffic = _load_traffic(input_path)
    result = compute_coverages(traffic)

    if output_json:
        _print_json(result)
    else:
        typer.echo(f"Method:            {result.method}")
        typer.echo(f"Total coverages:   {result.total_coverages:,.0f}")
        typer.echo(f"Design wheel load: {result.design_wheel_load_kn:.1f} kN")
        typer.echo(f"Confidence:        {result.confidence}")


@app.command()
def design(
    input_path: _InputPath,
    cbr: _CbrOption,
    curve_id: _CurveIdOption = "usace_cbr_v1",
    output_json: _JsonFlag = False,
) -> None:
    """Design pavement thickness (USACE CBR method)."""
    from haulpave.pavement import design_pavement

    traffic = _load_traffic(input_path)
    result = design_pavement(traffic, subgrade_cbr=cbr, curve_id=curve_id)

    if output_json:
        _print_json(result)
    else:
        typer.echo(f"Method:             {result.method}")
        typer.echo(f"Total CESA:         {result.total_cesa:,.0f}")
        typer.echo(f"Total coverages:    {result.total_coverages:,.0f}")
        typer.echo(f"Design wheel load:  {result.design_wheel_load_kn:.1f} kN")
        typer.echo(f"Required thickness: {result.required_thickness_mm:.0f} mm")
        typer.echo(f"Confidence:         {result.confidence}")


@app.command()
def compare(
    input_path: _InputPath,
    cbr: _CbrOption,
    curve_id: _CurveIdOption = "usace_cbr_v1",
    output_json: _JsonFlag = False,
) -> None:
    """Compare USACE CBR vs TRH 14 pavement design."""
    from haulpave.pavement import compare_methods

    traffic = _load_traffic(input_path)
    result = compare_methods(traffic, subgrade_cbr=cbr, curve_id=curve_id)

    if output_json:
        _print_json(result)
    else:
        typer.echo("=== USACE TM 5-822-12 ===")
        typer.echo(f"  Thickness: {result.usace.required_thickness_mm:.0f} mm")
        typer.echo(f"  CESA:      {result.usace.total_cesa:,.0f}")
        typer.echo(f"  Coverages: {result.usace.total_coverages:,.0f}")
        typer.echo("")
        typer.echo("=== TRH 14 (CSRA 1985) ===")
        typer.echo(f"  Thickness: {result.trh14.total_thickness_mm:.0f} mm")
        typer.echo(f"  G-class:   {result.trh14.material_class}")
        typer.echo(f"  Coverages: {result.trh14.total_coverages:,.0f}")
        typer.echo("")
        sign = "+" if result.delta_mm >= 0 else ""
        typer.echo(f"Delta (TRH14 − USACE): {sign}{result.delta_mm:.0f} mm")
        typer.echo(f"Subgrade CBR: {result.subgrade_cbr}%")


@app.command()
def economics(
    input_path: _InputPath,
    trips_per_day: _TripsPerDay = 0.0,
    working_days: _WorkingDays = 250,
    output_json: _JsonFlag = False,
) -> None:
    """Compute operating cost from a scenario JSON file."""
    from haulpave.economics.engine import compute_economics
    from haulpave.models.economics import CostScenario

    with input_path.open(encoding="utf-8") as f:
        data: Any = json.load(f)
    scenario = CostScenario.model_validate(data)
    result = compute_economics(
        scenario, trips_per_day=trips_per_day, working_days_per_year=working_days
    )

    if output_json:
        from dataclasses import asdict

        typer.echo(json.dumps(asdict(result), indent=2))
    else:
        typer.echo(f"Scenario:        {result.scenario_id}")
        typer.echo(f"Cost per trip:   ${result.cost_per_trip:,.2f}")
        typer.echo(f"Cost per t·km:   ${result.cost_per_tonne_km:.4f}")
        typer.echo(f"Annual cost:     ${result.annual_cost:,.2f}")
        typer.echo(f"Trips per year:  {result.trips_per_year:,.0f}")
        typer.echo(f"Confidence:      {result.confidence}")


@app.command()
def scenario(
    input_path: _InputPath,
    fuel_price: _FuelPrice = 0.80,
    working_days: _WorkingDays = 250,
    output_json: _JsonFlag = False,
) -> None:
    """Compare operating costs across road surface types (asphalt/gravel/concrete)."""
    from haulpave.economics.compare import ComparisonResult, RoadScenario, compare_scenarios

    with input_path.open(encoding="utf-8") as f:
        data: Any = json.load(f)
    roads = [RoadScenario.model_validate(r) for r in data]
    result = compare_scenarios(
        roads,
        fuel_price_usd_per_litre=fuel_price,
        working_days_per_year=working_days,
    )

    if output_json:
        typer.echo(result.model_dump_json(indent=2))
    else:
        typer.echo(f"{'Surface':>10}  {'Fuel ($/yr)':>14}  {'Tyres ($/yr)':>14}  {'Maint ($/yr)':>14}  {'Total ($/yr)':>14}")
        typer.echo("-" * 72)
        for sc in result.scenarios:
            total = sc.fuel_cost_usd_per_year + sc.tire_cost_usd_per_year + sc.maintenance_cost_usd_per_year
            typer.echo(
                f"{sc.name:>10}  {sc.fuel_cost_usd_per_year:>14,.0f}  "
                f"{sc.tire_cost_usd_per_year:>14,.0f}  "
                f"{sc.maintenance_cost_usd_per_year:>14,.0f}  "
                f"{total:>14,.0f}"
            )
        typer.echo(f"\nConfidence: {result.confidence}")


@app.command()
def export(
    input_path: _InputPath,
    output_path: _OutputPath,
    fuel_price: _FuelPrice = 0.80,
    working_days: _WorkingDays = 250,
) -> None:
    """Export scenario comparison to an Excel (.xlsx) workbook."""
    from haulpave.economics.compare import RoadScenario, compare_scenarios
    from haulpave.economics.export import export_comparison_to_excel

    with input_path.open(encoding="utf-8") as f:
        data: Any = json.load(f)
    roads = [RoadScenario.model_validate(r) for r in data]
    comp = compare_scenarios(
        roads,
        fuel_price_usd_per_litre=fuel_price,
        working_days_per_year=working_days,
    )
    saved = export_comparison_to_excel(comp, output_path)
    typer.echo(f"Exported to {saved}")


if __name__ == "__main__":
    app()  # pragma: no cover
