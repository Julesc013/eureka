# Software Heritage Connector Runtime Plan

This operations document mirrors the P92 planning-only audit pack. It explains the future Software Heritage connector runtime path while keeping runtime implementation blocked.

## Purpose

The future connector may, after explicit approval, process an approved bounded source-sync job and reviewed SWHID/origin/repository reference, fetch metadata-only Software Heritage identity/archive summaries, write public-safe source-cache candidates, emit evidence-ledger observation candidates, and never directly mutate the master index.

## Approval Gate

P76 exists, but `connector_approved_now` is false. Readiness is `blocked_connector_approval_pending`. There is no runtime, no external calls, and no approval claim.

## SWHID Policy Gate

SWHID syntax, object-type, provenance, privacy, and publication policy must be reviewed before future runtime work.

## Origin URL Policy Gate

Origin URL normalization and privacy review are required. Raw public query params, private origins, credentialed origins, local paths, localhost URLs, file URLs, uploaded files, arbitrary URLs, and unreviewed origin URLs remain forbidden.

## Repository Identity Gate

Repository owner/name/origin identity requires reviewed provenance, rename/transfer caution, credential stripping/rejection, and public-safe fingerprints for sensitive refs.

## Source-Code-Content Risk Gate

The future connector is metadata-only. There is no source code download, no content blob fetch, no directory traversal, no source archive download, no repository clone, no origin crawl, no source code execution, no source-code safety claim, and no source completeness claim.

## Token/Auth Boundary

V0 remains token-free and unauthenticated unless a future explicit policy approves otherwise. Software Heritage tokens and credentials are not configured.

## Why Runtime Is Not Implemented Yet

Approval, operator configuration, SWHID/origin/repository identity review, source-code-content risk review, Software Heritage source policy review, User-Agent/contact, rate-limit/timeout/retry/circuit-breaker, cache runtime, evidence runtime, and kill switch gates are incomplete.

## Runtime Architecture Plan

Future modules only: `client.py`, `identity_policy.py`, `content_policy.py`, `policy.py`, `normalize.py`, `evidence.py`, `errors.py`, and runtime docs under a future `runtime/connectors/software_heritage/` directory. P92 creates none of those runtime files.

Required future flags:

- EUREKA_SWH_CONNECTOR_ENABLED=0
- EUREKA_SWH_LIVE_CALLS_ENABLED=0
- EUREKA_SWH_AUTH_MODE=none
- EUREKA_SWH_TOKEN_ENABLED=0
- EUREKA_SWH_MAX_RESULTS=10
- EUREKA_SWH_TIMEOUT_MS=5000
- EUREKA_SWH_RATE_LIMIT_QPS=<operator-defined>
- EUREKA_SWH_USER_AGENT=<operator-defined>
- EUREKA_SWH_CONTACT=<operator-defined>
- EUREKA_SWH_SWHID_REVIEW_REQUIRED=1
- EUREKA_SWH_ORIGIN_REVIEW_REQUIRED=1
- EUREKA_SWH_REPOSITORY_IDENTITY_REVIEW_REQUIRED=1
- EUREKA_SWH_SOURCE_CODE_CONTENT_FETCH=0
- EUREKA_SWH_CONTENT_BLOB_FETCH=0
- EUREKA_SWH_DIRECTORY_CONTENT_FETCH=0
- EUREKA_SWH_REPOSITORY_CLONE=0
- EUREKA_SWH_SOURCE_ARCHIVE_DOWNLOAD=0
- EUREKA_SWH_ORIGIN_CRAWL=0
- EUREKA_SWH_CACHE_REQUIRED=1
- EUREKA_SWH_PUBLIC_SEARCH_FANOUT=0

## Future Source Sync Job Flow

1. Approved source sync job is selected.
2. Source policy guard checks connector approval.
3. SWHID/origin/repository identity guard validates approved identity source.
4. Source-code-content risk guard verifies metadata-only handling.
5. Token/auth guard verifies v0 is token-free unless future policy approves otherwise.
6. User-Agent/contact/rate-limit/timeout/circuit-breaker config is checked.
7. Connector performs bounded metadata-only request in future runtime.
8. Response is normalized to SWHID/origin/visit/snapshot/release/revision metadata summary.
9. Source cache record candidate is validated.
10. Evidence ledger observation candidate is built.
11. Candidate/evidence remains review-required.
12. No public index/master index mutation occurs.
13. Failures produce bounded error records, not raw payload dumps.

## Future Source Cache Outputs

- software_heritage_swhid_metadata_summary
- software_heritage_origin_metadata_summary
- software_heritage_visit_metadata_summary
- software_heritage_snapshot_metadata_summary
- software_heritage_release_metadata_summary
- software_heritage_revision_metadata_summary
- software_heritage_directory_metadata_summary
- software_heritage_archival_presence_summary

All are metadata summaries only: no raw payload dumps, no source-code content, no content blob fetches, no directory content traversal, no source archives, no repository clones, no origin crawls, no executable payloads, and no private data.

## Future Evidence Ledger Outputs

- software_identity_observation
- archival_presence_observation
- origin_metadata_observation
- visit_metadata_observation
- snapshot_metadata_observation
- release_metadata_observation
- revision_metadata_observation
- directory_metadata_observation
- SWHID_observation
- scoped_absence_observation

All observations remain `accepted_as_truth false`, review-required, and unable to claim rights clearance, license clearance, malware safety, source-code safety, source completeness, installability, or global absence.

## Public Search Boundary

Public search must not call Software Heritage live. Public search must not accept arbitrary SWHID/origin/repository params for live fetch. Public query params must not choose Software Heritage live mode. Future result cards may only show reviewed source-cache/evidence refs after a separate runtime and review path.

## Source Policy, User-Agent, Contact, And Rate-Limit Gates

Software Heritage API/source policy review is pending. User-Agent/contact is pending. Rate-limit, timeout, retry, and circuit-breaker values are pending. No operator contact details are fabricated here.

## Privacy, Rights, And Risk Posture

Metadata-only posture. No private repositories, private origins, token-required access, content blob fetch, raw file fetch, directory content traversal, source code download, source archive download, repository clone, origin crawl, source code execution, download, mirror, install, execute, rights clearance, license clearance, malware safety, source-code safety, source completeness, installability, private account access, credentials, raw payload dumps, private paths, or secrets.

## Prohibitions

No arbitrary SWHID/origin/repository fetch, no content/blob lookup, no directory traversal, no source-code fetch, no source-archive fetch, no repository-clone behavior, no public fanout, no mutation, no telemetry, and no credentials.

## Failure, Retry, And Circuit Breaker Model

Future runtime needs required timeouts, bounded retries, retry-after or abuse-limit respect, per-source circuit breakers, per-source rate limits, no retry storms, no public-search blocking, no raw error payload leaks, connector disablement on policy violation, and operator-visible failure summaries.

## Implementation Phases

Phase 0 keeps everything disabled. Phase 1 allows synthetic fixture-only local dry-run normalization. Phase 2 allows approved local live metadata probe only after human/operator approval and all gates. Phase 3 writes source-cache/evidence-ledger candidates through source sync worker. Phase 4 rebuilds public index from reviewed cache/evidence without live fanout. Phase 5 is hosted worker only with monitoring, rollback, quotas, and kill switch.

## Acceptance Criteria

- P76 approval complete
- SWHID policy reviewed
- origin URL policy reviewed
- repository identity policy reviewed
- source-code-content risk policy reviewed
- token/auth boundary reviewed
- source policy reviewed
- User-Agent/contact configured
- rate limits approved
- timeout approved
- retry/circuit-breaker values approved
- source sync worker runtime approved
- source-cache runtime approved
- evidence-ledger runtime approved
- cache destination configured
- evidence destination configured
- evidence attribution required
- public search fanout disabled
- arbitrary SWHID/origin/repository fetch disabled
- content blob fetch disabled
- directory content traversal disabled
- source code download disabled
- source archive download disabled
- repository clone disabled
- origin crawl disabled
- source code execution disabled
- kill switch present
- no download/mirror/install/execute
- no raw payload storage
- no credentials required for v0
- tests for blocked public params
- operator approval

## Next Steps

Proceed to P93 Object/Source/Comparison Page Runtime Planning v0. Keep Software Heritage runtime implementation blocked until P92 gates are explicitly satisfied.

This document is planning-only, with no runtime, no external calls, no arbitrary SWHID/origin/repository fetch, no source code/content/blob/repository clone behavior, and no mutation.
