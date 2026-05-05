# Object/Source/Comparison Page Runtime Plan

This P93 document plans future bounded, read-only, public-safe runtime pages for objects, sources, and comparisons. It is planning-only: no runtime routes, no renderer, no store, no live source calls, no public-search mutation, no source/evidence/candidate/master mutation, no downloads, no installers, no execution, no telemetry, and no accounts.

## Purpose

Future page runtime may render public-safe object, source, or comparison pages from controlled public-index or reviewed records. Pages explain evidence, limitations, conflicts, gaps, and safe next actions; they do not create truth.

## Readiness Gates

Readiness decision: `ready_for_local_dry_run_runtime_after_operator_approval`.

Object, source, and comparison page contracts validate. Public search, result-card, public index, and local public-search safety validate. Hosted runtime remains blocked because hosted backend is not configured and static deployment evidence remains failed.

## Why Runtime Is Not Implemented Yet

Operator approval is required. The safe page identifier policy must be accepted. Hosted runtime needs verified deployment evidence. Route tests for path traversal, arbitrary URL, local path, private cache access, and source selector abuse remain future work.

## Safe Page Identifier Policy

Future safe routes:

- /object/{object_id}
- /source/{source_id}
- /comparison/{comparison_id}
- /api/v1/object/{object_id}
- /api/v1/source-page/{source_id}
- /api/v1/comparison/{comparison_id}

Allowed IDs:

- public-index object IDs
- public-index source IDs
- public-index comparison IDs
- reviewed page IDs
- generated stable slugs derived from reviewed records

Forbidden IDs:

- local paths
- absolute paths
- arbitrary URLs
- raw source URLs
- unreviewed package names
- unreviewed repository names
- unreviewed SWHIDs
- unreviewed URI-R values
- uploaded filenames
- private cache keys
- secrets/tokens
- database paths

IDs must be normalized, bounded, public-safe, never interpreted as filesystem paths, and must never trigger live source calls.

## Runtime Architecture Plan

Future modules only: object page assembler, source page assembler, comparison page assembler, safe ID resolver, HTML/text/JSON renderer, privacy/action/source policy guard, stable error envelope, runtime docs, and a future public API route adapter. P93 creates none of those runtime files.

Required future flags:

- EUREKA_PAGE_RUNTIME_ENABLED=0
- EUREKA_OBJECT_PAGE_RUNTIME_ENABLED=0
- EUREKA_SOURCE_PAGE_RUNTIME_ENABLED=0
- EUREKA_COMPARISON_PAGE_RUNTIME_ENABLED=0
- EUREKA_PAGE_RUNTIME_SOURCE=public_index_only
- EUREKA_PAGE_RUNTIME_LIVE_SOURCE_CALLS=0
- EUREKA_PAGE_RUNTIME_DOWNLOADS=0
- EUREKA_PAGE_RUNTIME_INSTALLS=0
- EUREKA_PAGE_RUNTIME_EXECUTION=0
- EUREKA_PAGE_RUNTIME_TELEMETRY=0

## Object Page Plan

Input is `object_id` from public index or reviewed page record only. Output is HTML, text/lite, and JSON. Sections include identity, status/lane, versions/states/releases, representations, members, sources, evidence, compatibility, rights/risk/action posture, conflicts, absence/gaps, and limitations.

## Source Page Plan

Input is `source_id` from source inventory, public index, or reviewed page record only. Output is HTML, text/lite, and JSON. Sections include source identity, status, coverage, connector posture, policy/approval gates, cache/evidence posture, public search posture, limitations/gaps, and rights/risk/action posture.

## Comparison Page Plan

Input is `comparison_id` from public index or reviewed comparison record only. Future explicit compare requests need a separate contract and safety gate. Output is HTML, text/lite, and JSON. Sections cover subjects, criteria, matrix, identity/version/representation/source/evidence/compatibility comparisons, rights/risk/action comparison, conflicts/disagreements, absence/gaps, and limitations.

## Data Input Model

Allowed future inputs:

- public index documents
- generated public page records
- reviewed source inventory records
- reviewed connector approval records
- reviewed source cache records future
- reviewed evidence ledger records future
- candidate records only if labelled candidate/review-required
- known absence pages
- static fixture examples

Forbidden future inputs:

- arbitrary local paths
- arbitrary URLs
- private cache roots
- credentials
- user-uploaded files
- live source responses from request path
- raw unreviewed connector responses
- private query observations
- raw telemetry

## Response And Rendering Model

Future pages need an HTML baseline, text/lite output, JSON API response, stable error envelope, old-client-compatible markup, no required JavaScript, bounded page size, no private path leakage, no raw payload dumps, canonical link policy, provisional noindex policy where appropriate, future cache headers, accessibility basics, and source/evidence links.

## Static/Lite Fallback

Static demo pages remain available, lite/text pages work without JS, generated static pages can later be built from public-safe artifacts, hosted runtime must degrade to static/lite explanations, and backend-unavailable states must explain limitations.

## Public Search Integration

Future result cards may include object_page_ref, source_page_ref, or comparison_page_ref only after runtime verification. Result cards must not include live-source links unless reviewed. Page links read controlled page runtime only, never trigger new search or live probes, and remain disabled or absent until verified.

## Source/Evidence/Candidate Boundary

Source cache records are observations, evidence ledger records are evidence observations, and candidate records are provisional. Page runtime may render candidates only with labels, must not promote candidates, and must not mutate source/evidence/candidate records. Master index review remains separate.

## Privacy/Rights/Risk Posture

Public-safe data only. No private paths, secrets, private URLs, raw private query data, credentials, raw payload dumps, downloads, installers, execution, rights clearance, malware safety, installability claim, or unsafe action posture. Actions remain inspect/compare/cite only.

## Security/Abuse Concerns

Future runtime needs route ID length caps, charset policy, no path traversal, no arbitrary URL fetch, no local file access, no source selector that triggers live calls, no private cache access, stable error envelopes, hosted rate-limit/edge requirements, telemetry/account tracking off by default, and an operator kill switch.

## Implementation Phases

Phase 0 keeps disabled planning. Phase 1 is local dry-run assembler over synthetic examples with no routes. Phase 2 is local read-only routes from public index only. Phase 3 is hosted staging with safe route IDs and blocked-param tests. Phase 4 is public alpha page runtime links from public search. Phase 5 adds generated static snapshots for high-value records and offline/lite clients.

## Acceptance Criteria

- object page contract valid
- source page contract valid
- comparison page contract valid
- public search contract valid
- public search safety valid
- public index contract valid
- safe page ID policy accepted
- source/evidence/candidate boundary accepted
- privacy/action policy accepted
- hosted deployment evidence for hosted runtime
- route tests for path traversal/arbitrary URL/source selector blocked
- no downloads/install/execution
- no live source fanout
- no source/evidence/candidate/master mutation
- operator approval

## Next Steps

Proceed to P94 Pack Import Runtime Planning v0. Human/operator parallel remains hosted wrapper deployment, backend URL configuration, edge/rate limits, static verification, and Manual Observation Batch 0 Execution.

This document says planning-only/no runtime routes/no live source/no mutation.
