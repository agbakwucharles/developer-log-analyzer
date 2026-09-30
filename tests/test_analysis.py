from log_analyzer.analysis import analyze, percentile
from log_analyzer.parsers import parse_line


def test_access_parser_and_metrics() -> None:
    event = parse_line('127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /api/users HTTP/1.0" 500 2326 120')
    assert event is not None
    result = analyze([event])
    assert result["total_requests"] == 1
    assert result["error_rate"] == 1


def test_percentile() -> None:
    assert percentile([1, 2, 3, 4], 95) == 3.85
    assert parse_line("not a log") is None
