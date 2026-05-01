# Public Search Index Builder v0

Public Search Index Builder v0 generates the controlled index consumed by local
and future hosted public search.

## Commands

```powershell
python scripts/build_public_search_index.py --rebuild
python scripts/build_public_search_index.py --check
python scripts/build_public_search_index.py --json
python scripts/validate_public_search_index.py
python scripts/validate_public_search_index.py --json
python scripts/validate_public_search_index_builder.py
python scripts/validate_public_search_index_builder.py --json
python scripts/check_generated_artifact_drift.py --artifact public_search_index
```

`--rebuild` updates `data/public_index`. `--check` regenerates in a temporary
directory and fails if committed artifacts drift.

## Inputs

The builder reads only committed, governed fixture and recorded metadata:

- `control/inventory/sources/*.source.json`
- synthetic software fixtures
- GitHub Releases recorded fixtures
- Internet Archive recorded fixtures
- local bundle fixtures and synthetic member records
- article-scan recorded fixtures
- source expansion recorded fixtures

It does not read arbitrary local paths, private caches, staged packs, untracked
archives, user uploads, credentials, or live API responses.

## Output

The committed bundle is text-only JSON/NDJSON under `data/public_index`.
SQLite/FTS5 capability is detected and recorded, but no SQLite binary is
committed in v0.

## Safety

The index is `local_index_only`. It includes public-safe metadata and evidence
summaries only. It does not include executable payloads, raw binaries, downloads,
uploads, account data, telemetry, AI output, arbitrary URL fetches, or live
source probe results.

## Relationship To Hosting

P54's hosted wrapper now requires the committed public index to be present.
That makes the wrapper deployable by an operator without letting public requests
select local files or indexes. Deployment evidence remains separate and
operator-gated.
