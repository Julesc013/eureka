# IA Metadata Fixture Replay

IA-01 is fixture replay only. It reads committed JSON fixtures from
`examples/internet_archive_metadata/`, normalizes them into source-observation
candidate records, and emits boundary reports.

Run:

```powershell
python scripts/eureka_ia_fixture_replay.py --fixture-dir examples/internet_archive_metadata --json
python scripts/validate_ia_fixture_replay.py
```

## Fixture Classes

- `metadata_search_small`
- `item_metadata_read`
- `item_file_list_metadata_read`
- `missing_item`
- `malformed_partial`
- `retry_after_429`
- `large_file_list`
- `no_download_proof`

## Normalized Record Shape

Each replayed fixture emits:

- `source_id: internet_archive_metadata`
- `observation_id`
- `fixture_id`
- `observation_kind`
- metadata candidate fields
- file metadata candidate fields
- checksum candidate fields
- source locator
- limitations and risk flags
- `review_required: true`
- `accepted_truth: false`
- false side-effect flags for downloads, source cache, evidence, and index mutation

## Boundary Proof

Fixture replay proves no live source calls, source probes, source-cache writes,
evidence writes, candidate/reviewed/master index mutation, downloads/uploads,
model/provider calls, deployment, or production/public launch claim.

IA-02 remains a separate future task and requires explicit operator approval
before any live metadata probe.
