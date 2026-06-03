# INDEXLESS-LIVE-SEARCH-FALLBACK-00

Planned next task after `PUBLIC-ALPHA-REASSESS-06`.

Goal: add a governed live metadata fallback for public search when local,
snapshot, or index layers are unavailable.

Expected posture: resilience/degraded-mode search work only. Do not enable
public mutation, broad live source fanout, downloads, file fetches, OCR,
extraction, model calls, deployment, launch, or readiness claims without a
future reviewed task and explicit approval.
