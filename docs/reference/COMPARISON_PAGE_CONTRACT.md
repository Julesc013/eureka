# Comparison Page Contract v0

Comparison Page Contract v0 is a contract-only, evidence-first page contract for future public comparison pages. A comparison page explains how objects, versions, sources, representations, compatibility claims, evidence records, candidates, near misses, and conflicts compare.

A comparison page is not runtime yet. Comparison page is not ranking authority, comparison page is not candidate promotion, not a live connector page, not a source API proxy, not a downloader, not an installer, not an execution launcher, not a rights clearance decision, not a malware safety decision, and not production readiness.

Boundary rules:

- No runtime comparison pages.
- No live source calls.
- No source sync worker execution.
- No source cache mutation.
- No evidence ledger mutation.
- No candidate index mutation and no candidate promotion.
- No public index mutation, local index mutation, and no master index mutation.
- No download, no install, no execution, no upload, no mirror, and no arbitrary URL fetch.
- No rights clearance, no malware safety, no source trust authority, and no winner without evidence.

## Subjects, Types, Criteria, And Matrix

`subjects` requires at least two public-safe comparison subjects. Subjects can point to future object pages, source pages, public search results, public index documents, source cache records, evidence ledger records, candidate records, known absence pages, synthetic examples, or unknown placeholders.

`comparison_type` records whether the comparison is about identity, versions, source coverage, representations, members, compatibility, evidence strength, provenance, rights/risk/action posture, conflicts, absence/near misses, or candidate review. `winner_allowed` is false in v0 examples.

`criteria` records descriptive or categorical comparison dimensions. `comparison_matrix` contains cells with supported, unsupported, unknown, conflicting, not-applicable, or evidence-required status. `scoring_used_now`, `ranking_used_now`, and `winner_selected_now` must be false. `confidence_not_truth` must be true for matrix cells.

## Identity, Version, Representation, And Member Comparison

Identity comparison can express same-as, likely-same, variant-of, different, conflicting, or unknown. Duplicate handling preserves separate subjects unless a future review process says otherwise. `destructive_merge_allowed` must be false.

Version/state/release comparison is scoped. It can describe known, inferred, unknown, or conflicting versions, release dates, platforms, architectures, and lifecycle status. It does not create authoritative version truth.

Representation/member comparison is metadata-only in v0. `payload_included` and `downloads_enabled` must be false. Member paths, if present, must be public-safe synthetic or reviewed values and never private filesystem paths.

## Source, Evidence, Provenance, And Compatibility

Source/evidence/provenance comparison explains source roles, evidence status, provenance limits, and evidence-strength summaries. `accepted_as_truth` and `source_trust_claimed` must be false. Source cache and evidence ledger references are future projections only.

Compatibility comparison can show equivalent, more-specific, better-supported-by-evidence, conflicting, or unknown relations. `compatibility_claim_scoped` must be true, and compatibility cannot be claimed beyond evidence.

## Rights, Risk, Actions, Conflicts, And Gaps

Rights/risk/action comparison allows inspect metadata, view sources, view evidence, compare, and cite. Download, install, execute, upload, mirror, and arbitrary URL fetch are disabled.

Conflicts and disagreements are preserved. Near-miss and gap comparison records scoped absence, no verified result, mixed, or unknown states. `global_absence_claimed` must be false.

## Projections

Result-card/object/source projection is contract-only. Public search links, object page refs, and source page refs are future integration points and do not mutate public search or the public index.

API projection reserves future routes `/compare`, `/comparison/{comparison_id}`, `/api/v1/compare`, and `/api/v1/comparison/{comparison_id}` with `implemented_now: false`. Static projection is future-only in P81; no static comparison page demo artifact is generated.

## Privacy And Redaction

Public examples contain no private absolute paths, private URLs, raw private queries, account or user identifiers, IP addresses, credentials, secrets, API keys, executable payloads, raw payload dumps, or real binaries.

## Relationships And Deferred Work

Comparison pages relate to object pages, source pages, public search, public index, source cache, evidence ledger, candidate index, candidate promotion policy, known absence pages, identity resolution contracts, merge/deduplication contracts, and ranking contracts.

Runtime comparison pages, persistent page storage, public search comparison links, source/evidence runtime outputs, identity resolution runtime, result merge runtime, evidence-weighted ranking, compatibility-aware ranking, and hosted routes remain future work.
