"""HaulPave command-line interface.

Full CLI implemented in Phase 1 (Week 9–10).
"""

from __future__ import annotations

import typer

app = typer.Typer(
    name="haulpave",
    help="Pavement structure and operating-cost analysis for mine haul roads.",
    add_completion=False,
)


@app.command()
def version() -> None:
    """Print the HaulPave version."""
    from haulpave import __version__  # pragma: no cover

    typer.echo(f"HaulPave {__version__}")  # pragma: no cover


if __name__ == "__main__":
    app()  # pragma: no cover
