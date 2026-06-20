# Roadmap

The roadmap is staged so each step adds real product capability before it adds
public promises. Eureka's current priority is no longer public-alpha launch
preparation. The current priority is a local-first live Search/Hunt product
slice that can pass unseen-query acceptance.

## Current Gate

`EUREKA-REAL-LIVE-SEARCH-HUNT-00` is the active product gate:

```text
arbitrary live query
-> immediate transient web leads
-> deeper Hunt
-> safe page inspection
-> durable local Preview Index
-> restart
-> local search
```

Human acceptance remains blocked until all six live Search/Hunt milestones pass.
The existing public-alpha launch-candidate work is historical foundation, not
the current launch priority.

## Current Workable Baseline

- Local product loop present.
- Workbench local operator loop present.
- CLI, local web, and local HTTP API surfaces present.
- Provider-neutral live search contract and Brave adapter present.
- Normal search no longer silently substitutes hard-query fixtures.
- Portable bootstrap defaults to no demo data.
- Local `--live` provider calls are experimental, bounded, operator opt-in, and local only.
- Public-alpha read-only routes and snapshot/relay foundations remain present.
- No deployment, public launch, production readiness, public mutation, public live fanout, downloads, uploads, broad extraction, model calls, safe fetch, durable live indexing, or real Hunt completion is claimed.

## Near-Term Sequence

### 1. Retention And State Hotfix

Keep provider SearchLeads transient. Persist no Brave URLs, snippets, ranks, raw
responses, or credentials in Hunt summaries or indexes. Route CLI and HTTP
provider calls through one shared live service. Keep docs and AIDE memory aligned
with the local `--live` product objective.

### 2. Safe Web Fetching

Build an independent fetch pipeline for selected URLs with HTTP/HTTPS-only
requests, DNS and redirect revalidation, private-network blocking, robots
enforcement, MIME and size limits, timeouts, and honest fetch errors.

### 3. Durable SQLite/FTS Preview Index

Add an operational Preview Index store for independently fetched
SourceObservations while retaining immutable JSONL generation/export mechanics
for audit, replay, rollback, and distribution.

### 4. Real Hunt Engine

Expand Hunt from query variants into a budgeted loop: plan, provider search,
display transient leads, select fetch frontier, safe fetch, extract, dedupe,
index, follow links, and stop on budget, exhaustion, pause, or cancellation.

### 5. Usable Live Product UI

Keep normal pages focused on search, Hunt, result inspection, provenance,
retrieval/indexing state, and useful excerpts. Avoid queue terminology, review
packet language, raw JSON, and architecture exposition on the normal product
screen.

### 6. Unseen-Query Acceptance

Acceptance resumes only when an operator-chosen unseen query proves live
results, deeper Hunt, independent fetch, local unreviewed indexing, restart
retrieval, honest provider failure, no fixture substitution, no review
obstruction, no provider-result persistence, and no reviewed/public mutation.

## Later Tracks

### Second Provider Conformance

Add one additional provider family only after Brave-backed interactive Search
and Hunt are genuinely useful. Candidates include Internet Archive metadata,
Wayback CDX, GitHub Releases, or Software Heritage.

### Autonomous Index Foundry

After interactive Hunt works, add scheduled seed generation, stale observation
refresh, bounded surveys, source scorecards, clustering, Preview Index
generations, and review-batch preparation. The Foundry may update Preview state;
it may not create reviewed truth.

### Agentic Reasoning Layer

Only after deterministic Hunt is benchmarked, add typed agent proposals for
query planning, evidence extraction, identity hypotheses, conflict analysis,
next-probe planning, and safety critique. No agent bypasses policy, provenance,
or review.

### Review And Canonical Knowledge

Use real Hunts to produce useful PreviewDocuments, then route them through
ReviewItems, ReviewDecisions, ReviewedRecords, reviewed indexes, signed deltas,
and snapshots.

### Cooperative Eureka Network

Later, support ContributionPacks, validation, redaction, quarantine, staged
preview, review, signed deltas, and node synchronization.

### Public Service And Clients

After the local product and corpus prove their value, revisit public read-only
service, snapshot/relay, desktop, terminal, old-browser, mobile, institutional,
and agent-context clients. Downloads, installation, emulation, and
marketplace-like actions remain final gated layers.

## Roadmap Non-Claims

Roadmap entries are planned or gated work. They are not public launch,
deployment, production readiness, broad corpus coverage, rights clearance,
malware safety, native distribution readiness, or AI authority.
