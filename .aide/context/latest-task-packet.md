# Latest Task Packet

## TASK

IA-04 - IA Evidence Ledger Integration.

## PHASE

IA-04 completed as `PASS`.

## GOAL

Convert Internet Archive metadata source-cache records into local
evidence-ledger candidate records while preserving the evidence/review/index
boundary.

## WHY

IA-03 proved IA metadata observations can be written to source cache. IA-04
adds the next local-only handoff: source-cache records become evidence
candidates, but not accepted evidence or index records.

## ALLOWED_PATHS

- `runtime/evidence_ledger/**`
- `runtime/source_observation/internet_archive_evidence.py`
- `runtime/source_observation/internet_archive_source_cache.py`
- `scripts/eureka_ia_evidence_ledger_write.py`
- `scripts/validate_ia_evidence_ledger_integration.py`
- IA evidence policy, inventories, examples, docs, tests, audit pack, and AIDE
  queue/report metadata scoped to IA-04 and IA-05.

## FORBIDDEN_PATHS

- `eureka-instance/**`
- `instances/**`
- `.aide.local/**`
- `secrets/**`
- `.env`
- private local files, credentials, raw prompts, raw responses, and raw live IA
  response bodies
- `site/dist/**`
- `data/public_index/**`
- `runtime/connectors/**`
- `runtime/extraction/**`
- `runtime/search_quality/**`
- `native/**`
- `crates/**`

## IMPLEMENTATION

IA-04 adds:

- `control/policies/ia_evidence_ledger_policy.json`
- IA evidence record schema and write-plan inventories
- `runtime/source_observation/internet_archive_evidence.py`
- `scripts/eureka_ia_evidence_ledger_write.py`
- `scripts/validate_ia_evidence_ledger_integration.py`
- focused runtime and operations tests
- evidence examples, docs, inventories, and audit evidence

The IA adapter consumes IA source-cache records from fixture replay and the
redacted IA-02 live-preview path. It builds bounded evidence candidates for
title, mediatype, collection, creator, date, description, file metadata,
checksum metadata, source locator, and relation claims where present.

Durable ledger payloads are sanitized for the shared `runtime.evidence_ledger`
store, while IA audit records keep explicit boundary booleans.

## EVIDENCE

- `control/inventory/ia_04_result.json`
- `control/inventory/ia_evidence_boundary_report.json`
- `control/audits/ia-04-evidence-ledger-integration-v0/`
- `examples/evidence_ledger/internet_archive_metadata/expected_evidence_candidates.json`

## VALIDATION

- `python scripts/validate_ia_metadata_policy.py`
- `python scripts/validate_ia_fixture_replay.py`
- `python scripts/validate_ia_live_metadata_probe.py`
- `python scripts/validate_ia_source_cache_write.py`
- `python scripts/validate_ia_evidence_ledger_integration.py`
- focused IA evidence runtime and operations tests

## BOUNDARIES

- evidence candidates require review
- accepted truth created: false
- operator instance mutated: false
- raw response committed: false
- candidate index mutated: false
- reviewed index mutated: false
- master index mutated: false
- downloads/uploads/extraction/model/deployment: false

## NEXT

IA-05 - IA Candidate Index Integration.

## NON_GOALS

- no new live IA probe
- no downloads or uploads
- no source sync
- no extraction
- no model/provider calls
- no candidate, reviewed, or master index mutation
- no production or public launch readiness claim

## ACCEPTANCE

- evidence policy, schema, adapter, CLI, validator, docs, examples, and audit
  pack exist
- dry-run passes
- temp-instance evidence write passes
- fixture and live-preview evidence candidates are written to temp
- all evidence candidates require review
- no accepted truth or index mutation is created

## OUTPUT_SCHEMA

Final IA-04 report follows the user-requested `STATUS`, `SUMMARY`,
`COMMITS`, `IA_EVIDENCE`, `VALIDATION`, `BOUNDARIES`, and `NEXT_TASK`
sections.

## CONTEXT_REFS

- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`

## TOKEN_ESTIMATE

Approximate packet tokens: 900.
