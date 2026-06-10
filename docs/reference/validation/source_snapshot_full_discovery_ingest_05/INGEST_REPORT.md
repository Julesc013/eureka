# Ingest Report

## External Run

| Field | Value |
|---|---|
| run id | `source_snapshot_full_discovery_rerun_05` |
| command | `python -m unittest discover -s tests -t .` |
| status | `fail` |
| exit code | `1` |
| started at | `2026-06-10T14:33:07Z` |
| updated at | `2026-06-10T15:20:53Z` |
| duration seconds | `2866.304682` |
| tests run | `5643` |
| failures | `39` |
| errors | `0` |
| skipped | `0` |

## Currentness

The compact summary reports:

```text
branch: dev
head: 9200df49f084cf313cccf821bf56f0194376f202
working_tree_clean: true
```

The current repo `HEAD` during ingest was the same hash. The summary is current
to the checked-out `dev` HEAD.

## Failure Posture

No import or discovery crash was reported. The full discovery command completed
and produced compact artifacts.

The 39 failures are validator expectation failures concentrated around older
HUNT, LOCAL, public-alpha-defer, and historical `dev -> main` validator tests
whose expected queue or promotion state no longer matches the current product
queue:

```text
current_recommended_task: WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE
```

Default action for this task is ingest and classification only. No same-turn
repair was performed.

