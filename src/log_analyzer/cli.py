from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer
from rich import print

from .analysis import analyze, filter_events
from .parsers import parse_file
from .report import write_html

app = typer.Typer(no_args_is_help=True)


def summary(path: Path, json_output: bool = False, start: str | None = None, end: str | None = None, status: int | None = None, method: str | None = None, route: str | None = typer.Option(None, "--path")) -> dict[str, object]:
    parsed = parse_file(path)
    events = filter_events(parsed.events, start=datetime.fromisoformat(start) if start else None, end=datetime.fromisoformat(end) if end else None, status=status, method=method, path=route)
    result = {"parse": {"parsed_lines": parsed.parsed_lines, "skipped_lines": parsed.skipped_lines}, **analyze(events)}
    if json_output: typer.echo(json.dumps(result, indent=2, default=str))
    else: print(result)
    return result


@app.command("analyze")
def analyze_file(path: Path, json_output: bool = typer.Option(False, "--json")) -> None: summary(path, json_output)
@app.command()
def errors(path: Path, json_output: bool = typer.Option(False, "--json")) -> None: summary(path, json_output)
@app.command()
def endpoints(path: Path, json_output: bool = typer.Option(False, "--json")) -> None: summary(path, json_output)
@app.command()
def performance(path: Path, json_output: bool = typer.Option(False, "--json")) -> None: summary(path, json_output)
@app.command()
def status(path: Path, json_output: bool = typer.Option(False, "--json")) -> None: summary(path, json_output)
@app.command()
def ips(path: Path, json_output: bool = typer.Option(False, "--json")) -> None: summary(path, json_output)
@app.command()
def report(path: Path, output: Path) -> None: write_html(summary(path, True), output)
