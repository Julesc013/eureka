"""Deterministic local discovery capacity baseline harness."""

from __future__ import annotations

from pathlib import Path
import statistics
import tempfile
import time
import tracemalloc
from typing import Any, Mapping, Sequence

from runtime.index.preview import SQLitePreviewIndexStore


BASELINE_SCHEMA = "eureka.discovery_capacity_baseline.v0"


def run_capacity_baseline(
    *,
    dataset_sizes: Sequence[int] = (1000, 10000),
    work_root: str | Path | None = None,
    query_iterations: int = 20,
    export_generation: bool = True,
) -> dict[str, Any]:
    sizes = [max(1, min(int(size), 100000)) for size in dataset_sizes] or [1000]
    root = Path(work_root) if work_root else Path(tempfile.mkdtemp(prefix="eureka-capacity-"))
    root.mkdir(parents=True, exist_ok=True)
    tracemalloc.start()
    started_all = time.perf_counter()
    datasets = []
    for size in sizes:
        datasets.append(_run_one(root, size=size, query_iterations=query_iterations, export_generation=export_generation))
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "schema_version": BASELINE_SCHEMA,
        "status": "pass",
        "work_root": str(root),
        "dataset_sizes": sizes,
        "datasets": datasets,
        "total_duration_ms": _elapsed_ms(started_all),
        "memory_high_water_bytes": int(peak),
        "provisional_v0_targets": _targets(datasets),
        "production_scale_claimed": False,
        "network_provider_calls": False,
        "model_provider_calls": False,
    }


def _run_one(root: Path, *, size: int, query_iterations: int, export_generation: bool) -> dict[str, Any]:
    dataset_root = root / f"dataset-{size}"
    db_path = dataset_root / "preview.sqlite"
    dataset_root.mkdir(parents=True, exist_ok=True)
    create_started = time.perf_counter()
    store = SQLitePreviewIndexStore(db_path)
    creation_ms = _elapsed_ms(create_started)
    records = [_observation(index) for index in range(size)]
    insert_started = time.perf_counter()
    upsert = store.upsert_observations(records)
    bulk_insert_ms = _elapsed_ms(insert_started)
    incremental_started = time.perf_counter()
    store.upsert_observations([_observation(size + 1)])
    incremental_upsert_ms = _elapsed_ms(incremental_started)
    query_durations = []
    for index in range(max(1, min(int(query_iterations or 20), 100))):
        query_started = time.perf_counter()
        store.search(f"artifact {index % max(1, size)}", limit=10)
        query_durations.append(_elapsed_ms(query_started))
    exact_started = time.perf_counter()
    store.search("ExactTitle 1", limit=10)
    exact_title_ms = _elapsed_ms(exact_started)
    phrase_started = time.perf_counter()
    store.search('"legacy driver"', limit=10)
    phrase_ms = _elapsed_ms(phrase_started)
    facet_started = time.perf_counter()
    stats = store.stats()
    faceted_status_ms = _elapsed_ms(facet_started)
    export_ms = 0
    backup_bytes = 0
    if export_generation:
        export_started = time.perf_counter()
        export = store.export_generation(dataset_root / "generation")
        export_ms = _elapsed_ms(export_started)
        manifest = Path(str(export.get("current_path") or ""))
        backup_bytes = manifest.stat().st_size if manifest.exists() else 0
    db_bytes = db_path.stat().st_size if db_path.exists() else 0
    store.close()
    return {
        "schema_version": "eureka.discovery_capacity_dataset.v0",
        "dataset_size": size,
        "database_creation_ms": creation_ms,
        "bulk_insert_ms": bulk_insert_ms,
        "incremental_upsert_ms": incremental_upsert_ms,
        "fts_query_latency_ms": _summary(query_durations),
        "exact_title_query_ms": exact_title_ms,
        "phrase_query_ms": phrase_ms,
        "faceted_status_query_ms": faceted_status_ms,
        "generation_export_ms": export_ms,
        "backup_manifest_bytes": backup_bytes,
        "document_count": int(stats.get("document_count") or 0),
        "database_bytes": db_bytes,
        "database_bytes_per_document": round(db_bytes / max(1, int(stats.get("document_count") or 1)), 2),
        "network_provider_calls": False,
        "production_scale_claimed": False,
        "upsert_status": upsert.get("status"),
    }


def _observation(index: int) -> dict[str, Any]:
    return {
        "observation_id": f"obs:{index:08d}",
        "canonical_url": f"https://example.test/artifacts/{index}",
        "final_url": f"https://example.test/artifacts/{index}",
        "content_hash": f"hash-{index:08d}",
        "title": f"ExactTitle {index} legacy driver artifact",
        "extracted_title": f"ExactTitle {index}",
        "extracted_text": f"artifact {index} legacy driver manual platform version date benchmark text",
        "retrieved_at": "2026-06-21T00:00:00Z",
        "run_id": "benchmark",
        "query": f"artifact {index}",
        "source_family": "synthetic_benchmark",
        "outbound_links": [],
        "provider_result_payload_persisted": False,
    }


def _summary(values: Sequence[int]) -> dict[str, int]:
    if not values:
        return {"p50": 0, "p95": 0, "p99": 0}
    ordered = sorted(values)
    return {"p50": _pct(ordered, 50), "p95": _pct(ordered, 95), "p99": _pct(ordered, 99)}


def _pct(values: Sequence[int], pct: int) -> int:
    if not values:
        return 0
    index = min(len(values) - 1, max(0, round((pct / 100) * (len(values) - 1))))
    return int(values[index])


def _targets(datasets: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    fts_p95 = [int((item.get("fts_query_latency_ms") or {}).get("p95") or 0) for item in datasets]
    upsert = [int(item.get("incremental_upsert_ms") or 0) for item in datasets]
    return {
        "local_fts_p95_ms": max(25, int(statistics.median(fts_p95 or [0]) * 4) or 25),
        "incremental_upsert_ms": max(25, int(statistics.median(upsert or [0]) * 4) or 25),
        "ten_k_document_startup_ms": "measure_on_local_hardware",
        "backup_target_ms": "measure_with_backup_command",
        "foundry_checkpoint_target_ms": "measure_with_foundry_stage",
        "target_type": "provisional_v0_not_production_slo",
    }


def _elapsed_ms(started: float) -> int:
    return max(0, int((time.perf_counter() - started) * 1000))
