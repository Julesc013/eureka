# Pack Import Runtime Plan

P94 is planning-only. It explains a future bounded, local-first, validate-first, quarantine-first pack import runtime without implementing that runtime.

## Purpose

The future runtime would accept only approved repo examples or operator-approved local packs, validate them, quarantine/stage them after approval, inspect them, emit import reports and candidate diffs, and stop before mutation. Pack claims remain untrusted until review and promotion.

## Readiness Gates

- source pack contract valid
- evidence pack contract valid
- index pack contract valid
- contribution pack contract valid
- pack set validator valid
- validate-only import tool valid
- import report contract valid
- local quarantine/staging model valid
- staging report path contract valid
- local staging manifest valid
- staged-pack inspector valid
- master index review queue contract valid
- privacy/path/secret policy accepted
- executable payload/content safety policy accepted
- mutation/promotion boundary accepted
- operator approval

## Why Runtime Is Not Implemented Yet

No pack import runtime is implemented because mutation, staging, quarantine, promotion, public contribution intake, and operator policy must stay explicitly gated. P94 adds no runtime files, no database tables, no persistent queues, no uploads, no admin endpoints, no URL fetching, no execution, and no mutation.

## Pack Input And Trust Model

Allowed future origins are repo canonical examples, local operator-approved packs, and later signed/reviewed packs after separate contracts. Forbidden origins include public uploads, arbitrary URLs, web downloads, private cache roots, arbitrary local filesystem trees, executable installers, package manager output, live connector responses, and raw user telemetry.

## Validation Pipeline

The future pipeline locates an approved root, verifies path containment, checks manifests, schemas, pack kind, checksums, forbidden fields, privacy/path/secret posture, executable payload policy, pack-kind validators, pack-set validators, validate-only import report, and candidate diff report, then stops before mutation.

## Quarantine, Staging, And Inspection

Quarantine roots must be operator approved and not user-controlled request parameters. Staging paths are deterministic and bounded. The staged-pack inspector reads metadata and reports only. No pack content execution, URL fetching, deep archive extraction, import, index mutation, or promotion is allowed.

## Import Report And Diff Model

Reports include pack identity, kind, validation status, privacy/path/secret scan status, executable/content policy status, expected candidate effects, source cache candidate effects, evidence ledger candidate effects, candidate index candidate effects, public/master index effects, conflicts, missing prerequisites, review requirements, and no-mutation guarantees. Effects are candidate/dry-run only.

## Source/Evidence/Index/Contribution/Pack Set Plans

Source pack import validates source identity and connector posture without live source calls or cache/index mutation. Evidence pack import preserves evidence/provenance and conflicts with `accepted_as_truth` false. Index pack import is compare-only and never replaces indexes. Contribution pack import reports review queue candidates without accounts, public intake, or automatic acceptance. Pack set import validates ordering, references, and conflicts with no mutation.

## Privacy, Path, And Secret Policy

Reject absolute paths, path traversal, private cache roots, home/user paths, credentials, secrets, API keys, tokens, private URLs, and public-example identifiers. Normalize paths as pack-internal logical paths only. Do not scan local files beyond the approved pack root.

## Executable Payload And Content Safety

No execution, installers, scripts, package manager invocation, emulator/VM launch, binary inspection beyond metadata, deep archive extraction, or malware safety claim. Executable references require risk labels and remain out of scope unless separately governed.

## Rights, Risk, And Provenance

Source terms apply. Pack license metadata is not rights clearance. Evidence provenance is preserved. Claims are not truth. Malware safety is not claimed. Conflicts are preserved. Manual/human review is required before promotion.

## Mutation And Promotion Boundary

Validate-only import may produce reports. Quarantine may stage candidate material only after approval. Promotion is separate from import. Source cache, evidence ledger, candidate index, public index, local index, and master index mutation each require separate approval and must not be bypassed.

## Public Contribution Boundary

P94 does not implement public contribution intake, upload endpoints, accounts, moderation runtime, or public pack submission. Public contribution requires separate contribution runtime, abuse policy, storage policy, privacy policy, and review workflow.

## Failure, Rollback, And Audit

Future runtime must emit failed validation reports, allow quarantine discard and staging cleanup, avoid partial mutation in v0, define transactional boundaries later, record command results, expose stable operator-visible errors, support reproducible validation, and avoid private audit data.

## Implementation Phases

Phase 0 keeps runtime disabled. Phase 1 local dry-run reports canonical examples only. Phase 2 local quarantine/staging over operator-approved packs. Phase 3 local review queue candidate generation. Phase 4 explicit promotion after separate approval. Phase 5 hosted/private maintainer workflow. Phase 6 public contribution intake only after separate governance.

## Acceptance Criteria

Before implementation: all pack contracts, validators, validate-only import, quarantine/staging, staged inspector, review queue, privacy/path policy, executable policy, mutation boundary, rollback/audit model, no public upload, no execution, no URL fetching, no mutation by default, and operator approval must be satisfied.

## Next Steps

Recommended next branch: P95 Deep Extraction Contract v0. Do not start pack import local dry-run runtime until explicit operator approval and mutation/promotion gates exist.
