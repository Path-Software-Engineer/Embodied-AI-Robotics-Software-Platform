"""Bounded local HTTP latency smoke; not a production capacity benchmark."""

from __future__ import annotations

import json
import os
import time
import urllib.request

BASE = "http://127.0.0.1:8000"


def sample(path: str, body: dict | None = None) -> tuple[float, dict]:
    headers = {"Content-Type": "application/json", "X-Actor-Id": "sprint2-benchmark"}
    if body is not None:
        headers["Authorization"] = f"Bearer {os.environ['EMBODIED_OPERATOR_TOKEN']}"
    request = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers,
        method="POST" if body is not None else "GET",
    )
    started = time.perf_counter_ns()
    with urllib.request.urlopen(request, timeout=10) as response:
        payload = json.load(response)
    return (time.perf_counter_ns() - started) / 1_000_000, payload


def percentiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "p50": round(ordered[(len(ordered) * 50 - 1) // 100], 2),
        "p95": round(ordered[(len(ordered) * 95 - 1) // 100], 2),
        "p99": round(ordered[(len(ordered) * 99 - 1) // 100], 2),
    }


def main() -> None:
    if len(os.environ.get("EMBODIED_OPERATOR_TOKEN", "")) < 32:
        raise RuntimeError("operator token required for local benchmark")
    read_ms: list[float] = []
    plan_ms: list[float] = []
    run_id = ""
    for _ in range(20):
        duration, status = sample("/api/v2/control/status")
        read_ms.append(duration)
        run_id = status["run_id"]
    for _ in range(10):
        duration, result = sample("/api/v2/plans", {"target_radians": 0.1})
        if result["plan"]["run_id"] != run_id:
            raise RuntimeError("benchmark proposal crossed simulation runs")
        plan_ms.append(duration)
    read = percentiles(read_ms)
    plan = percentiles(plan_ms)
    result = {
        "profile": "local_single_client_smoke",
        "run_id": run_id,
        "read_samples": len(read_ms),
        "plan_persist_samples": len(plan_ms),
        "read_ms": read,
        "plan_persist_ms": plan,
        "budget_p95_ms": {"read": 2000, "plan_persist": 3000},
    }
    print(json.dumps(result))
    if read["p95"] > 2000 or plan["p95"] > 3000:
        raise RuntimeError("local control API latency exceeded smoke budget")


if __name__ == "__main__":
    main()
