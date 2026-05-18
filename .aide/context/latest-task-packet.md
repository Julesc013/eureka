# Latest Task Packet

## TASK

IA-03 - IA Source Cache Write Path.

## PHASE

IA-03 completed as `PASS`.

## GOAL

Add the first local source-cache write path for Internet Archive metadata
observations using IA-01 fixture replay records and IA-02 redacted normalized
live-probe preview records.

## WHY

IA-02 produced a successful verified metadata-only IA response and a redacted
normalized preview, but IA-03 was still needed before any downstream evidence
work could rely on a local persisted source-observation cache. The source cache
is the required intermediate store before future IA-04 evidence integration.

## ALLOWED_PATHS

- `runtime/source_cache/**`
- `runtime/source_observation/internet_archive_source_cache.py`
- IA metadata observation helpers already in `runtime/source_observation/`
- `scripts/eureka_ia_source_cache_write.py`
- `scripts/validate_ia_source_cache_write.py`
- IA policy, inventory, docs, tests, examples, audit pack, and AIDE queue/report
  metadata scoped to IA-03 and IA-04.

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

IA-03 adds an IA source-cache policy, record schema inventory, adapter, CLI,
validator, expected examples, focused tests, docs, inventories, and audit pack.

The adapter builds IA-specific source-cache records and writes sanitized durable
source-cache entries through the existing `runtime.source_cache.SourceCacheStore`
API. The generic cache entry avoids reserved public-truth fields while the IA
record and audit evidence preserve explicit non-claim flags.

The CLI defaults to dry-run. Apply mode requires `--apply`, an explicit
`--instance`, and a configured operator token. Validation proves apply against a
temporary explicit local instance only.

## EVIDENCE

- `control/policies/ia_source_cache_policy.json`
- `control/inventory/ia_source_cache_record_schema.json`
- `control/inventory/ia_source_cache_fixture_write_result.json`
- `control/inventory/ia_source_cache_live_preview_write_result.json`
- `control/inventory/ia_source_cache_boundary_report.json`
- `control/inventory/ia_03_result.json`
- `control/audits/ia-03-source-cache-write-path-v0/`

## CONTEXT_REFS

- `.aide/context/repo-map.json`
- `.aide/context/test-map.json`
- `.aide/context/context-index.json`
- `.aide/context/latest-context-packet.md`
- `control/inventory/ia_02_result.json`
- `control/inventory/ia_02_tls_continue_normalized_preview.json`
- `control/inventory/ia_02_next_task_decision.json`
- `.aide/queue/IA-03/task.yaml`
- `.aide/queue/IA-04/task.yaml`
- `.aide/queue/index.yaml`
- `docs/operations/IA_SOURCE_CACHE_WRITE_RUNBOOK.md`
- `docs/reference/IA_SOURCE_CACHE_RECORD.md`

## VALIDATION

Focused validation passed:

- IA metadata policy validator
- IA fixture replay validator
- IA live-probe validator
- IA source-cache write validator
- IA source-cache CLI dry-run
- IA source-cache focused unittest modules
- architecture boundary checks

Generated artifact cleanliness should be checked after commit because the audit
pack is generated evidence and appears as drift before it is committed.

## NON_GOALS

- No new live IA call.
- No raw response body commit.
- No operator instance mutation.
- No evidence ledger write.
- No candidate, reviewed, or master index mutation.
- No downloads/uploads.
- No extraction, model/provider calls, deployment, production readiness claim,
  or public launch claim.

## ACCEPTANCE

Status is `PASS`.

- Source-cache policy, schema, adapter, CLI, validator, tests, docs, examples,
  inventories, and audit pack exist.
- Dry-run passes.
- Temp-instance source-cache write passes.
- Fixture and live-preview records are written to temp source cache.
- IA-04 is the recommended next task.

## OUTPUT_SCHEMA

Final response sections:

- `STATUS`
- `SUMMARY`
- `COMMITS`
- `IA_SOURCE_CACHE`
- `VALIDATION`
- `BOUNDARIES`
- `NEXT_TASK`

## TOKEN_ESTIMATE

Approximate task packet tokens: 950.
