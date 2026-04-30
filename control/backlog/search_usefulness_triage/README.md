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

The live audit has been re-run through Article/Scan Fixture Pack v0 and Manual
External Baseline Observation Pack v0. Current Search Usefulness Audit v0
reports:

- total queries: 64
- covered: 5
- partial: 22
- source_gap: 26
- capability_gap: 9
- unknown: 2
- external baselines pending: Google 64, Internet Archive metadata 64, Internet Archive full text/OCR 64
- planner_gap: 24
- query_interpretation_gap: 21

## Decisions

- Primary usefulness wedge: old-platform-compatible software search
- Secondary usefulness wedge: member-level discovery inside bundles
- Immediate next milestone: Manual Observation Batch 0

Update: Source Coverage and Capability Model v0 and Real Source Coverage Pack
v0 are implemented, and Old-Platform Software Planner Pack v0 now improves
deterministic old-platform interpretation. Member-Level Synthetic Records v0
then added bounded member target refs and parent lineage, and Result Lanes +
User-Cost Ranking v0 added deterministic member-vs-parent usefulness
annotations. Compatibility Evidence Pack v0 then added bounded source-backed
compatibility evidence while preserving unknown outcomes. Search Usefulness
Audit Delta v0 recorded the first measured movement, and Old-Platform Source
Coverage Expansion v0 then expanded committed old-platform fixture coverage.
Search Usefulness Audit Delta v1 recorded the new movement. Hard Eval
Satisfaction Pack v0 then moved five archive hard tasks from `not_satisfied`
to `partial` using source-backed structured evidence without weakening hard
task definitions. The next milestone is Old-Platform Result Refinement Pack v0
because the remaining blocker is expected-lane, bad-result, and result-shape
scoring for those partials.
Old-Platform Result Refinement Pack v0 then added deterministic result-shape,
expected-lane, and bad-result checks. One driver/member hard task is now
satisfied, four old-platform hard tasks remain partial, and the next milestone
is More Source Coverage Expansion v1 because exact-release, concrete identity,
direct-artifact, and source-evidence breadth gaps still block the selected
wedge.
More Source Coverage Expansion v1 then added targeted tiny fixture evidence
for Firefox XP, a blue FTP-client XP candidate, Windows 98 registry repair, and
Windows 7 utility/app hard-eval gaps. Current archive evals report
`capability_gap=1` and `satisfied=5`; the next milestone is Article/Scan
Fixture Pack v0 because `article_inside_magazine_scan` remains the only archive
hard capability gap.
Article/Scan Fixture Pack v0 then added one tiny synthetic article-scan fixture
source with parent issue lineage, page-range metadata, and OCR-like fixture
text. Current archive evals report `satisfied=6`; the next milestone is Manual
External Baseline Observation Pack v0 because all external baselines remain
pending/manual.
Manual External Baseline Observation Pack v0 then added the governed
manual-only baseline system registry, observation schema/template,
instructions, pending manifest, validator, and status report under
`evals/search_usefulness/external_baselines/`. It seeds 192 pending slots
across 64 queries and three systems without recording observed baselines. The
next milestone is Manual Observation Batch 0.
Public Search Rehearsal v0 then established local/prototype public search
evidence, and Search Usefulness Source Expansion v2 now adds six fixture-only
recorded source families plus 15 tiny metadata records to the local corpus.
The broad Search Usefulness Audit moved from `covered=5`, `partial=22`,
`source_gap=26`, `capability_gap=9`, `unknown=2` to `covered=5`,
`partial=40`, `source_gap=10`, `capability_gap=7`, `unknown=2` without live
probes, scraping, crawling, URL fetching, external observations, real binaries,
downloads, uploads, local path search, hosted search, or production relevance
claims. Search Usefulness Delta v2 now records that movement under
`control/audits/search-usefulness-delta-v2/`, including selected query
movement, source-family impact, current failure modes, hard-eval status,
public-search smoke status, external-baseline pending status, and remaining
gaps. The next milestone is Source Pack Contract v0.

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
