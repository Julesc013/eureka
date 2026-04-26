# Search Usefulness Audit v0

Search Usefulness Audit v0 is a repo-level evaluation harness for asking a
large, practical question: how useful is Eureka today for archive-resolution
style searches, and which failures should drive future backend work?

It is not a claim that Eureka beats Google, Internet Archive, or other broad
search systems. Current Eureka is expected to lose many queries on corpus
breadth and live source coverage. The audit records those losses as source,
index, planner, decomposition, representation, compatibility, actionability,
or UX gaps instead of hiding them.

## Scope

- `query.schema.yaml`: JSON-subset YAML schema for query fixtures.
- `observation.schema.yaml`: JSON-subset YAML schema for manual or generated
  per-system observations.
- `report.schema.yaml`: JSON-subset YAML schema for suite reports.
- `queries/`: first broad query pack for the audit.
- `observations/`: manual external baseline observations may be recorded here
  later.
- `reports/`: report guidance; generated reports are not committed by default.

The v0 pack contains 64 queries across current covered sanity checks, platform
software, latest-compatible releases, drivers, manuals, article-inside-scan
tasks, package/container/member tasks, vague identity queries, web-archive
dead-link queries, source-code/package-release queries, and negative/absence
queries.

## External Baseline Policy

The audit runner does not scrape Google, Internet Archive, or any other
external system. External baselines are emitted as
`pending_manual_observation` until a human operator records observations later.

Manual observation templates can be created with:

```bash
python scripts/record_search_baseline_observation.py --query windows_7_apps --system google
```

## Running

```bash
python scripts/run_search_usefulness_audit.py
python scripts/run_search_usefulness_audit.py --json
python scripts/run_search_usefulness_audit.py --query windows_7_apps
```

The report aggregates current Eureka statuses, pending external baselines,
failure modes, and future-work labels. It does not introduce ranking, fuzzy
retrieval, vector search, LLM planning, live crawling, or production benchmark
claims.

## Backlog Triage

Search Usefulness Backlog Triage v0 lives under
`control/backlog/search_usefulness_triage/`.

The triage selects old-platform-compatible software search as the primary
usefulness wedge and member-level discovery inside bundles as the secondary
wedge. It keeps external Google and Internet Archive baselines pending manual
observation and selected Source Coverage and Capability Model v0 as the next
implementation milestone at the time of triage.

Source Coverage and Capability Model v0 now exists as the metadata/projection
layer needed by that recommendation. Real Source Coverage Pack v0 adds tiny
recorded Internet Archive-like metadata/file-list fixtures plus a committed
local bundle fixture corpus. Old-Platform Software Planner Pack v0 now reduces
planner/query-interpretation gaps by making OS aliases, latest-compatible
intent, driver/hardware intent, vague identity uncertainty, documentation
intent, and member-discovery hints explicit. Member-Level Synthetic Records v0
now makes selected committed local-bundle members visible as deterministic
member target refs with parent lineage and evidence. Audit deltas remain
intentionally bounded: external Google and Internet Archive baselines remain
pending manual observation, and the audit still performs no live-source
crawling, no Google scraping, no Internet Archive scraping, and no external
baseline fabrication.
