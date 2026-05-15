"""Latency helpers for local route checks."""

from __future__ import annotations

import time
from typing import Any, Mapping


def now_counter() -> float:
    return time.perf_counter()


def record_elapsed_ms(started: float, finished: float | None = None) -> float:
    end = time.perf_counter() if finished is None else finished
    return round(max(end - started, 0.0) * 1000.0, 3)


def summarize_latency(results: list[Mapping[str, Any]]) -> dict[str, Any]:
    values: list[dict[str, Any]] = []
    for result in results:
        elapsed = result.get("elapsed_ms")
        if isinstance(elapsed, (int, float)):
            values.append(
                {
                    "suite": result.get("suite", ""),
                    "case_id": result.get("case_id", ""),
                    "path": result.get("path", ""),
                    "elapsed_ms": float(elapsed),
                }
            )
    ordered = sorted(values, key=lambda item: item["elapsed_ms"], reverse=True)
    total = sum(item["elapsed_ms"] for item in values)
    return {
        "schema_version": "local_eval_latency_summary.v0",
        "status": "pass",
        "route_count": len(values),
        "max_elapsed_ms": ordered[0]["elapsed_ms"] if ordered else 0.0,
        "average_elapsed_ms": round(total / len(values), 3) if values else 0.0,
        "slowest_routes": ordered[:5],
        "strict_latency_gate_enabled": False,
        "warnings": [],
        "limitations": ["latency values are local smoke estimates only"],
    }
