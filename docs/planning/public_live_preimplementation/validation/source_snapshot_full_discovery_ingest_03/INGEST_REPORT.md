# Ingest Report

## Run

| Field | Value |
|---|---|
| run id | `source_snapshot_full_discovery_rerun_03` |
| branch | `dev` |
| head | `2549af51a4f472e6fae9a825af2275b27f8556b8` |
| command | `python -m unittest discover -s tests -t .` |
| status | `fail` |
| tests run | `5620` |
| failures | `22` |
| errors | `0` |
| summary current to HEAD | `true` |
| repo clean before run | `true` |

## External Artifacts

Artifacts remain outside the repo:

```text
D:\Projects\Eureka\eureka-test-runs\source_snapshot_full_discovery_rerun_03\status.json
D:\Projects\Eureka\eureka-test-runs\source_snapshot_full_discovery_rerun_03\full_unittest_summary.json
D:\Projects\Eureka\eureka-test-runs\source_snapshot_full_discovery_rerun_03\failure_families.json
D:\Projects\Eureka\eureka-test-runs\source_snapshot_full_discovery_rerun_03\failed_tests.txt
```

## Ingest Decision

The source/snapshot full-discovery validation gate remains blocked.

The next repair should target historical queue-validator drift.
