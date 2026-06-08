# Ingest Report

## Run

| Field | Value |
|---|---|
| run id | `source_snapshot_full_discovery_rerun_02` |
| branch | `dev` |
| head | `5ada452b524cd27ff061dd47c5e9b4fa2319d7c7` |
| command | `python -m unittest discover -s tests -t .` |
| status | `pass` |
| tests run | `5508` |
| failures | `0` |
| errors | `0` |
| skipped | `0` |
| summary current to HEAD | `true` |
| repo clean before run | `true` |
| repo clean after run | `true` |

## External Artifacts

Artifacts remain outside the repo:

```text
D:\Projects\Eureka\eureka-test-runs\source_snapshot_full_discovery_rerun_02\status.json
D:\Projects\Eureka\eureka-test-runs\source_snapshot_full_discovery_rerun_02\full_unittest_summary.json
D:\Projects\Eureka\eureka-test-runs\source_snapshot_full_discovery_rerun_02\full_unittest.log
```

## Ingest Decision

The source/snapshot full-discovery validation gate can be closed as green and
current for this HEAD.

Public alpha remains blocked by corpus/artifact/readiness gates.

`dev -> main` remains blocked pending dedicated promotion review.

