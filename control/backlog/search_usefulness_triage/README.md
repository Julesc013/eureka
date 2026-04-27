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

The live audit has been re-run through Old-Platform Source Coverage Expansion v0. Current Search Usefulness Audit v0 reports:

- total queries: 64
- covered: 5
- partial: 20
- source_gap: 28
- capability_gap: 9
- unknown: 2
- external baselines pending: Google 64, Internet Archive metadata 64, Internet Archive full text/OCR 64
- planner_gap: 24
- query_interpretation_gap: 21

## Decisions

- Primary usefulness wedge: old-platform-compatible software search
- Secondary usefulness wedge: member-level discovery inside bundles
- Immediate next milestone: Search Usefulness Audit Delta v1

Update: Source Coverage and Capability Model v0 and Real Source Coverage Pack
v0 are implemented, and Old-Platform Software Planner Pack v0 now improves
deterministic old-platform interpretation. Member-Level Synthetic Records v0
then added bounded member target refs and parent lineage, and Result Lanes +
User-Cost Ranking v0 added deterministic member-vs-parent usefulness
annotations. Compatibility Evidence Pack v0 then added bounded source-backed
compatibility evidence while preserving unknown outcomes. Search Usefulness
Audit Delta v0 recorded the first measured movement, and Old-Platform Source
Coverage Expansion v0 then expanded committed old-platform fixture coverage.
The next milestone is Search Usefulness Audit Delta v1 so the repo can record
the new movement without weakening queries or fabricating external baselines.

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
