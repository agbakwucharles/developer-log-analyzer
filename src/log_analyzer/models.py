from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LogEvent(BaseModel):
    timestamp: datetime | None = None
    level: str | None = None
    method: str | None = None
    path: str | None = None
    status_code: int | None = None
    duration_ms: float | None = None
    ip: str | None = None
    request_id: str | None = None
    message: str | None = None
    exception_type: str | None = None


class ParseResult(BaseModel):
    events: list[LogEvent]
    parsed_lines: int = 0
    skipped_lines: int = 0
