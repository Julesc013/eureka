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

The six deterministic implementation milestones are present, but automated
live acceptance is still blocked on `OPERATOR-LIVE-CANARY-00`, and human
product acceptance remains a separate operator verdict. The current internal
hardening wave is `EUREKA-LIVE-PRODUCT-HARDENING-AND-ACCEPTANCE-WAVE-03`.
The existing public-alpha launch-candidate work is historical foundation, not
the current launch priority.

## Current Workable Baseline

- Local product loop present.
- Workbench local operator loop present.
- CLI, local web, and local HTTP API surfaces present.
- Provider-neutral live search contract and Brave adapter present.
- Normal search no longer silently substitutes hard-query fixtures.
- Portable bootstrap defaults to no demo data.
- Safe fetch, local SQLite/FTS Preview Index, deterministic Hunt, live UX,
  second-provider conformance, disabled Foundry v0, and live-discovery audit
  foundations are implemented deterministically.
- Local `--live` provider calls are experimental, bounded, operator opt-in, and local only.
- Public-alpha read-only routes and snapshot/relay foundations remain present.
- No deployment, public launch, production readiness, public mutation, public
  live fanout, downloads, uploads, broad extraction, model calls, accepted live
  canary, human usefulness approval, or production scale is claimed.

## Near-Term Sequence

### 1. Wave 03 Product Hardening

Finish safe internal work before the operator canary: capability-state
reconciliation, observability, diagnostics, recovery, backup, migration,
performance baselines, Foundry operator controls, declarative provider policy,
portable local bundle rehearsal, canary closeout, human rehearsal, external full
discovery handoff, and a hardening audit.

### 2. Operator Live Canary

Run the bounded real canary with a local Brave key. It must prove real live
results, Hunt, policy-approved independent fetch, SourceObservation,
PreviewDocument, restart, local retrieval, no provider-result persistence, and
no reviewed/public mutation.

### 3. Human Product Acceptance

After the live canary passes, the operator tests the actual product with unseen
queries and records an explicit human verdict. Automation must not fill this in.

### 4. External Full Discovery

Full unittest discovery remains an operator/CI lane outside normal AI sessions.

### 5. Agentic Planner Preflight

Only after real live canary, human acceptance, external full discovery, and a
clean hardening audit should an agentic Hunt Planner preflight be recommended.

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
