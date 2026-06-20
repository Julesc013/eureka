# Existing Eval Seams

The oracle retains and composes existing local seams:

- `evals/hard_queries/**`: primary known-answer fixture source.
- `runtime/engine/evals/**`: compatible eval result vocabulary, retained for existing consumers.
- `runtime/resolution_run/**`: E2E runner and replay bundle validation.
- `runtime/index/preview/**`: Preview Index build/search/validation.
- `runtime/local/e2e_hunt_exploration.py`: Workbench exploration projection.
- `runtime/local/synthetic_truth_path.py`: isolated synthetic truth and rollback path.
- `runtime/surface/**`: JSON, text, HTML-basic, and snapshot renderer projections.
- `runtime/snapshots/**`: snapshot verification seam.
- Existing public-alpha, no-mutation, generated-output, and architecture tests remain guardrails.

Disposition:

- retain existing consumers;
- adapt through deterministic oracle product adapters;
- do not rewrite runtime eval modules for neatness;
- do not replace full unittest discovery.
