# Pack Import Pipeline

Pack Import Pipeline v0 is an architecture plan for future local import of
source, evidence, index, and contribution packs. It is planning only and does
not implement import. It also does not implement staging, indexing, upload,
submission, or master-index mutation.

This plan does not implement import.

## Purpose

Future import should let a user explicitly select one governed pack and run it
through validation before anything else can happen. Imported records stay
claims, candidates, or summaries; they do not become canonical truth.

## Pipeline

1. User explicitly selects a pack.
2. Pack Import Validator Aggregator v0 identifies pack type from the manifest.
3. The aggregate validator runs the matching individual validator.
4. Tool validates checksums and declared JSON/JSONL files.
5. Tool classifies privacy, rights, and risk posture.
6. Tool emits an import report.
7. Future tools either stop at validate-only, stage locally, or reject/quarantine.

The first future implementation should be `validate_only`. The next possible
mode is `stage_local_quarantine`.

P40 implements the aggregate validation step through
`scripts/validate_pack_set.py`. It validates known examples or one explicit
pack root and still does not implement import, staging, indexing, upload, or
master-index mutation.

Pack Import Report Format v0 now defines the durable report envelope for step
6. `contracts/packs/pack_import_report.v0.json`,
`examples/import_reports/`, and `scripts/validate_pack_import_report.py`
record validation outcomes, privacy/rights/risk issues, provenance, next
actions, and hard false mutation fields. This does not implement import. It
does not stage packs. It does not mutate local index state, runtime state,
or public search. It does not mutate the master index. It does not upload or
submit anything.
It does not mutate local index state.
It does not mutate the master index.

AI Provider Contract v0 is adjacent but not part of import runtime. Future AI
outputs can be validated as typed suggestions through
`scripts/validate_ai_output.py` before they draft contributions, but the import
pipeline must not trust AI output as canonical truth or mutate
search/master-index state from it. Typed output validation is not pack import,
staging, evidence import, contribution import, or master-index acceptance.

## Staging

Future staging roots are logical and private by default:

- `.eureka-local/staged_packs/`
- `.eureka-local/quarantine/`
- `.eureka-local/import_reports/`

These roots must not be under `site/dist`, `external`, or public data. P39 does
not create these directories.

## Search And Index Boundaries

Validate-only and local quarantine have no search impact by default and no
index impact by default. Source, evidence, and index packs must not affect the
`local_index_only` public runtime until an explicit later import/index milestone
creates a guarded opt-in mode.

Hosted public search and the static public site are unaffected by local pack
import planning.

## Master Index Boundary

Pack import is local. Master-index review is separate. Accepted public records
need Master Index Review Queue decisions, provenance, conflict handling, and
policy review. Import never creates automatic acceptance.

## Not Implemented

This plan does not implement source/evidence/index/contribution pack import,
local index mutation, canonical registry mutation, uploads, accounts, hosted
master index writes, executable plugins, live fetch, scraping, crawling,
downloads, installers, native clients, relay runtime, or snapshot reader
runtime.
