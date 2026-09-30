from __future__ import annotations

from collections import Counter
from datetime import datetime
from statistics import mean

from .models import LogEvent


def filter_events(events: list[LogEvent], *, start: datetime | None = None, end: datetime | None = None, status: int | None = None, method: str | None = None, path: str | None = None) -> list[LogEvent]:
    return [event for event in events if (start is None or event.timestamp is None or event.timestamp >= start) and (end is None or event.timestamp is None or event.timestamp <= end) and (status is None or event.status_code == status) and (method is None or event.method == method) and (path is None or event.path == path)]


def analyze(events: list[LogEvent], limit: int = 10) -> dict[str, object]:
    requests = [event for event in events if event.method]
    statuses = Counter(event.status_code for event in requests if event.status_code is not None)
    durations = [event.duration_ms for event in requests if event.duration_ms is not None]
    failures = [event for event in requests if event.status_code and event.status_code >= 400]
    endpoint_counts = Counter(event.path for event in requests if event.path)
    endpoint_duration: dict[str, list[float]] = {}
    for event in requests:
        if event.path and event.duration_ms is not None: endpoint_duration.setdefault(event.path, []).append(event.duration_ms)
    errors = [event for event in events if event.level and event.level.lower() in {"error", "fatal"}] + failures
    return {"total_requests": len(requests), "requests_by_endpoint": top(endpoint_counts, limit), "requests_by_method": top(Counter(event.method for event in requests if event.method), limit), "status_codes": dict(sorted(statuses.items())), "status_groups": {"2xx": sum(count for code, count in statuses.items() if 200 <= code < 300), "3xx": sum(count for code, count in statuses.items() if 300 <= code < 400), "4xx": sum(count for code, count in statuses.items() if 400 <= code < 500), "5xx": sum(count for code, count in statuses.items() if 500 <= code < 600)}, "error_rate": len(failures) / len(requests) if requests else 0, "performance": {"average_ms": mean(durations) if durations else None, "median_ms": percentile(durations, 50), "p95_ms": percentile(durations, 95), "p99_ms": percentile(durations, 99), "slowest_requests": sorted(([event.model_dump(mode="json") for event in requests if event.duration_ms is not None]), key=lambda item: item["duration_ms"], reverse=True)[:limit], "slowest_endpoints": sorted(((path, mean(values)) for path, values in endpoint_duration.items()), key=lambda item: item[1], reverse=True)[:limit]}, "errors": {"count": len(errors), "messages": top(Counter(event.message for event in errors if event.message), limit), "exceptions": top(Counter(event.exception_type for event in errors if event.exception_type), limit), "failing_endpoints": top(Counter(event.path for event in failures if event.path), limit)}, "ips": top(Counter(event.ip for event in requests if event.ip), limit)}


def top(counts: Counter[str] | Counter[int], limit: int) -> list[tuple[str | int, int]]: return [(key, count) for key, count in counts.most_common(limit)]
def percentile(values: list[float], point: int) -> float | None:
    if not values: return None
    ordered = sorted(values); index = (len(ordered) - 1) * point / 100; low = int(index); high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)
