from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from .models import LogEvent, ParseResult

ACCESS = re.compile(r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d{3}) \S+(?: "[^"]*" "[^"]*")?(?: (?P<duration>\d+(?:\.\d+)?))?')


def parse_file(path: str | Path) -> ParseResult:
    events: list[LogEvent] = []; skipped = 0
    with Path(path).open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            event = parse_line(line)
            if event: events.append(event)
            elif line.strip(): skipped += 1
    return ParseResult(events=events, parsed_lines=len(events), skipped_lines=skipped)


def parse_line(line: str) -> LogEvent | None:
    text = line.strip()
    if not text: return None
    if text.startswith("{"):
        try: return parse_json(json.loads(text))
        except (json.JSONDecodeError, ValueError, TypeError): return None
    match = ACCESS.fullmatch(text)
    if not match: return None
    values = match.groupdict()
    try: timestamp = datetime.strptime(values["time"], "%d/%b/%Y:%H:%M:%S %z")
    except ValueError: timestamp = None
    return LogEvent(timestamp=timestamp, ip=values["ip"], method=values["method"], path=values["path"], status_code=int(values["status"]), duration_ms=float(values["duration"]) if values["duration"] else None)


def parse_json(value: dict[str, object]) -> LogEvent:
    timestamp = as_datetime(value.get("timestamp") or value.get("time"))
    return LogEvent(timestamp=timestamp, level=as_string(value.get("level")), method=as_string(value.get("method")), path=as_string(value.get("path") or value.get("endpoint")), status_code=as_int(value.get("status_code") or value.get("status")), duration_ms=as_float(value.get("duration_ms") or value.get("duration")), ip=as_string(value.get("ip") or value.get("remote_addr")), request_id=as_string(value.get("request_id")), message=as_string(value.get("message")), exception_type=as_string(value.get("exception_type") or value.get("exception")))


def as_string(value: object) -> str | None: return str(value) if value is not None else None
def as_int(value: object) -> int | None: return int(value) if isinstance(value, (str, int, float)) else None
def as_float(value: object) -> float | None: return float(value) if isinstance(value, (str, int, float)) else None
def as_datetime(value: object) -> datetime | None:
    if not isinstance(value, str): return None
    try: return datetime.fromisoformat(value)
    except ValueError: return None
