from __future__ import annotations

import html
import json
from pathlib import Path


def write_html(summary: dict[str, object], path: str | Path) -> None:
    payload = html.escape(json.dumps(summary, indent=2, default=str))
    Path(path).write_text(f"<html><head><title>Log analysis report</title><style>body{{font-family:system-ui;max-width:960px;margin:3rem auto}}pre{{background:#f4f4f5;padding:1rem;overflow:auto}}</style></head><body><h1>Log analysis report</h1><pre>{payload}</pre></body></html>", encoding="utf-8")
