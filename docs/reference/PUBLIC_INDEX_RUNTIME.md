# Public Index Runtime

`runtime.public_index` exposes the local reviewed-index runtime.

## Store

`PublicIndexStore.open(path)` opens an explicit SQLite database path or `:memory:` for tests. The store initializes schema with `init()`, writes reviewed records with `write_record()`, writes rebuild metadata with `write_rebuild()`, reads with `get_record()` and `list_records()`, searches with `search()`, creates local absence reports with `absence_report()`, and validates store health with `check_integrity()`.

## Records

`PublicIndexRecord` contains the reviewed record, normalized fields, searchable text, source cache reference, evidence reference, review item reference, review decision reference, limitations, and warnings.

`PublicIndexRebuild` records the rebuild inputs, included and excluded counts, included statuses, target database, dry-run state, limitations, and warnings.

`PublicIndexSearchResult` is a local search result with matched terms and score.

`PublicIndexAbsenceReport` describes a local no-result outcome for a query and lists checked sources plus limitations.

`PublicIndexSummary` reports local table counts.

## Rebuild

`rebuild_reviewed_public_index(source_cache_db, evidence_ledger_db, review_queue_db, public_index_db, include_statuses=("accepted",), dry_run=False)` reads explicit input stores and writes only the explicit reviewed-index store when `dry_run` is false.

## Validation

The validation helpers reject hidden/private output roots, generated site output roots, reserved control vocabulary, and public-acceptance payload fields. The runtime does not import connector, local-foundry, network, browser, provider, or subprocess modules.
