# Search Usefulness Backlog Triage v0

Search Usefulness Backlog Triage v0 converts Search Usefulness Audit v0 and the Comprehensive Test/Eval Audit findings into a ranked future-work backlog.

This pack is governance only. It does not change runtime behavior, add source connectors, add live crawling, scrape Google or Internet Archive, add ranking/fuzzy/vector/LLM retrieval, port Rust behavior, add app work, or make production-readiness claims.

## Inputs

- `evals/search_usefulness/`
- `scripts/run_search_usefulness_audit.py`
- `runtime/engine/evals/search_usefulness_runner.py`
- `control/audits/2026-04-25-comprehensive-test-eval-audit/`
- `tests/hardening/`
- `control/inventory/sources/`

The live audit was re-run after Old-Platform Software Planner Pack v0. Current Search Usefulness Audit v0 reports:

- total queries: 64
- covered: 5
- partial: 4
- source_gap: 41
- capability_gap: 12
- unknown: 2
- external baselines pending: Google 64, Internet Archive metadata 64, Internet Archive full text/OCR 64
- planner_gap: 24
- query_interpretation_gap: 21

## Decisions

- Primary usefulness wedge: old-platform-compatible software search
- Secondary usefulness wedge: member-level discovery inside bundles
- Immediate next milestone: Member-Level Synthetic Records v0

Update: Source Coverage and Capability Model v0 and Real Source Coverage Pack
v0 are implemented, and Old-Platform Software Planner Pack v0 now improves
deterministic old-platform interpretation. The next implementation milestone is
Member-Level Synthetic Records v0 because member target refs and parent lineage
are now the visible bottleneck for support-CD, ISO, ZIP, and bundle queries.

## Contents

- `TRIAGE_SUMMARY.md`
- `QUERY_FAILURE_MATRIX.md`
- `SOURCE_COVERAGE_PRIORITIES.md`
- `PLANNER_GAP_PRIORITIES.md`
- `MEMBER_DISCOVERY_PRIORITIES.md`
- `COMPATIBILITY_EVIDENCE_PRIORITIES.md`
- `NEXT_10_TASKS.md`
- `SELECTED_WEDGES.md`
- `REJECTED_OR_DEFERRED_WORK.md`
- `backlog_item.schema.json`
- `backlog_items.json`
