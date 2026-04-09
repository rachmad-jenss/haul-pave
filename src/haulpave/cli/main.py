"""HaulPave command-line interface.

Commands:
  version    — Print the HaulPave version.
  cesa       — Compute CESA from a traffic JSON file.
  coverages  — Compute design coverages from a traffic JSON file.
  design     — Run USACE CBR pavement design.
  compare    — Run USACE vs TRH 14 comparison.
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


if __name__ == "__main__":
    app()  # pragma: no cover
