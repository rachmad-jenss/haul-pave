# CLI Module

Module: `src/haulpave/cli/`

Command-line interface built with [Typer](https://typer.tiangolo.com/).

---

## Commands

### `haulpave version`

Print the HaulPave version.

**Source:** `src/haulpave/cli/main.py:43`

### `haulpave cesa --input <path> [--json]`

Compute Cumulative Equivalent Standard Axles (CESA) from a traffic JSON file.

**Source:** `src/haulpave/cli/main.py:57`

| Option | Description |
|--------|-------------|
| `--input`, `-i` | Path to traffic JSON file |
| `--json` | Output as formatted JSON (default: human-readable text) |

### `haulpave coverages --input <path> [--json]`

Compute design coverages (USACE TM 5-822-12) from a traffic JSON file.

**Source:** `src/haulpave/cli/main.py:76`

| Option | Description |
|--------|-------------|
| `--input`, `-i` | Path to traffic JSON file |
| `--json` | Output as formatted JSON (default: human-readable text) |

### `haulpave design --input <path> --cbr <value> [--curve-id <id>] [--json]`

Design pavement thickness using the USACE CBR method.

**Source:** `src/haulpave/cli/main.py:96`

| Option | Description |
|--------|-------------|
| `--input`, `-i` | Path to traffic JSON file |
| `--cbr` | Subgrade CBR [%] |
| `--curve-id` | Curve dataset ID (default `"usace_cbr_v1"`) |
| `--json` | Output as formatted JSON (default: human-readable text) |

### `haulpave compare --input <path> --cbr <value> [--curve-id <id>] [--json]`

Compare USACE CBR vs TRH 14 pavement design side-by-side.

**Source:** `src/haulpave/cli/main.py:120`

| Option | Description |
|--------|-------------|
| `--input`, `-i` | Path to traffic JSON file |
| `--cbr` | Subgrade CBR [%] |
| `--curve-id` | Curve dataset ID (default `"usace_cbr_v1"`) |
| `--json` | Output as formatted JSON (default: human-readable text) |
