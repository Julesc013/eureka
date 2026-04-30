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
- `external_baselines/`: governed manual-only observation protocol, baseline
  system registry, templates, instructions, pending slots, and validation for
  Google and Internet Archive comparisons.
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

Manual External Baseline Observation Pack v0 now adds a stricter governed
workflow under `external_baselines/`. It defines manual-only systems for Google
web search, Internet Archive metadata search, and Internet Archive full-text/OCR
search; a JSON observation schema and template; operator instructions; and a
pending manifest covering all 64 queries across the three systems. The
validator and status report are:

```bash
python scripts/validate_external_baseline_observations.py
python scripts/validate_external_baseline_observations.py --json
python scripts/report_external_baseline_status.py
python scripts/report_external_baseline_status.py --json
```

The pack performs no scraping, automated external querying, live Internet
Archive API calls, or web API calls. External baselines remain pending until a
human records observations with operator, timestamp, exact query, visible
result, usefulness, and limitation metadata. One manual observation is
time-sensitive and not global Google or Internet Archive truth.

Manual Observation Batch 0 now lives under
`external_baselines/batches/batch_0/`. It selects 13 high-value old-platform,
member-discovery, driver/support-media, and article/scan query IDs across the
three manual-only baseline systems, producing 39 batch-scoped pending slots.
It is preparation only: it records no observed external results, performs no
searches, scrapes nothing, automates nothing, and leaves the global 192
external baseline slots pending until a human fills records later.

Manual Observation Entry Helper v0 adds local helper scripts for the human
entry workflow:

```bash
python scripts/list_external_baseline_observations.py --batch batch_0
python scripts/create_external_baseline_observation.py --batch batch_0 --query-id windows_7_apps --system-id google_web_search --stdout
python scripts/validate_external_baseline_observations.py --file <path>
python scripts/report_external_baseline_status.py --batch batch_0 --next-pending
```

These helpers only list slots, create pending fillable JSON, validate files,
and summarize progress. They do not perform observations, scrape or automate
Google or Internet Archive, fetch URLs, open browsers, fill top results, or
count templates/pending slots as observed baselines.

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

Result Lanes + User-Cost Ranking v0 now adds bounded lane and user-cost details
to current Eureka observations when search/index results provide them. The audit
may use those fields to explain actionability or member-vs-parent cost, but it
does not treat them as production relevance ranking and it still leaves
external baselines pending unless manually recorded.

Compatibility Evidence Pack v0 now adds bounded source-backed compatibility
evidence fields to current Eureka observations when fixture metadata, member
paths, README text, or compatibility notes support them. The audit may use
those fields to explain compatibility-evidence gaps, but it still does not
execute software, verify installers, call live sources, or fabricate Google or
Internet Archive baseline observations.

Search Usefulness Audit Delta v0 now lives under
`control/audits/search-usefulness-delta-v0/`. It records the current audit
counts after the source/planner/member/lane/compatibility sequence, compares
them with a historical reported aggregate baseline, and recommends
Old-Platform Source Coverage Expansion v0 because source coverage remains the
dominant gap. The delta pack is audit/reporting only; it does not change
retrieval behavior or record external baseline observations.

Old-Platform Source Coverage Expansion v0 now expands the committed
Internet-Archive-shaped and local bundle fixture corpus. The current local
audit reports `covered=5`, `partial=20`, `source_gap=28`, `capability_gap=9`,
and `unknown=2`. The movement is source-backed and bounded: Google and
Internet Archive baselines remain pending manual observation, and the audit
still performs no live-source crawling, scraping, fuzzy/vector retrieval, LLM
planning, or production benchmark comparison.

Search Usefulness Audit Delta v1 now lives under
`control/audits/search-usefulness-delta-v1/`. It records the measured movement
after the source expansion against the v0 delta baseline: `partial +15`,
`source_gap -13`, `capability_gap -2`, and archive eval movement to
`capability_gap=1` plus `not_satisfied=5`. The pack is measurement/reporting
only; it does not change retrieval behavior or mark any external baseline
observed.

Hard Eval Satisfaction Pack v0 now lives under
`control/audits/hard-eval-satisfaction-v0/`. It is archive-eval focused and
moves five hard tasks to `partial` through source-backed structured evidence
mapping; it does not change this broader 64-query audit corpus or external
baseline posture.

Old-Platform Result Refinement Pack v0 now lives under
`control/audits/old-platform-result-refinement-v0/`. It refines archive hard
eval result-shape, lane, and bad-result checks, moving one driver/member task
to `satisfied` while leaving four old-platform tasks partial. It does not
change the 64-query Search Usefulness Audit corpus, retrieval behavior, or
external baseline posture.

More Source Coverage Expansion v1 now lives under
`control/audits/more-source-coverage-expansion-v1/`. It adds targeted tiny
recorded/fixture-only source material for Firefox XP, a blue FTP-client XP
candidate, Windows 98 registry repair, and Windows 7 utility/app evidence. The
current local audit reports `covered=5`, `partial=21`, `source_gap=27`,
`capability_gap=9`, and `unknown=2`; external baselines remain pending manual
observation and the audit still adds no live crawling, scraping, fuzzy/vector
retrieval, LLM behavior, or production benchmark claims.

Article/Scan Fixture Pack v0 now lives under
`control/audits/article-scan-fixture-pack-v0/`. It adds one tiny
synthetic/recorded article-scan fixture with parent issue lineage, page-range
metadata, and OCR-like fixture text. The current local audit reports
`covered=5`, `partial=22`, `source_gap=26`, `capability_gap=9`, and
`unknown=2`; external baselines remain pending manual observation and the audit
still adds no live source calls, scraping, OCR, PDF/image parsing, real scans,
fuzzy/vector retrieval, LLM behavior, or production benchmark claims.

Manual External Baseline Observation Pack v0 now lives under
`evals/search_usefulness/external_baselines/`. It adds schema, templates,
instructions, pending slots, validation, and status reporting for manual Google
and Internet Archive observations. It changes no retrieval behavior and records
no observed external baselines by itself.

Manual Observation Batch 0 now adds the first prioritized pending batch under
`evals/search_usefulness/external_baselines/batches/batch_0/`. It prepares 39
query/system slots for later human observation across Google web search,
Internet Archive metadata search, and Internet Archive full-text/OCR search.
It does not perform observations or change Eureka search behavior.

Manual Observation Entry Helper v0 now adds stdlib-only listing, creation,
file-validation, and Batch 0 progress helpers for those pending slots. It does
not perform observations, fetch URLs, open browsers, or fabricate external
baseline results.

Search Usefulness Source Expansion v2 now lives under
`control/audits/search-usefulness-source-expansion-v2/`. It adds six
fixture-only recorded source families and 15 tiny metadata records for selected
Wayback/Memento, Software Heritage, SourceForge, package registry, manual, and
review/description gaps. The current local audit reports `covered=5`,
`partial=40`, `source_gap=10`, `capability_gap=7`, and `unknown=2`, moving
selected source and capability gaps into honest partial coverage without live
source calls. External Google and Internet Archive baselines remain pending
manual observation, and the audit still adds no live probing, URL fetching,
scraping, crawling, real binaries, downloads, local path search, fuzzy/vector
retrieval, LLM behavior, or production benchmark claim.

Search Usefulness Delta v2 now lives under
`control/audits/search-usefulness-delta-v2/`. It measures the Source Expansion
v2 effect using the committed P32 report as baseline: `partial` increased by
18, `source_gap` decreased by 16, `capability_gap` decreased by 2, and
`covered`/`unknown` stayed unchanged. Exact failure-mode deltas are marked
unavailable because the pre-P32 failure-mode baseline was not committed as
machine-readable JSON. External baselines remain pending/manual.

Source Pack Contract v0 is now implemented as the next safe extension layer:
validated source metadata packs can be authored and checked locally, but they
are not imported into this audit, indexed, uploaded, or accepted into a master
index. Evidence Pack Contract v0 is also implemented as the claim/observation
layer: validated evidence packs can be authored and checked locally, but they
are not imported into this audit, indexed, uploaded, accepted into a master
index, or treated as canonical truth. Index Pack Contract v0 is now implemented
as the coverage/record-summary layer: validated index packs can describe what
was indexed, but they are not imported, merged, uploaded, accepted into a
master index, exported as raw SQLite/cache files, or treated as canonical
truth. Contribution Pack Contract v0 is now implemented as the review-candidate
wrapper: validated contribution packs can reference source/evidence/index packs
and propose corrections, aliases, compatibility notes, absence reports, or
result feedback, but they are not uploaded, imported, automatically accepted, or
treated as canonical truth. Master Index Review Queue Contract v0 is now
implemented as the governance layer for future queue entries and decisions, but
it still does not import packs or affect audit results. Future usefulness work
should use Source/Evidence/Index Pack Import Planning v0 before pack import
affects audit results.
