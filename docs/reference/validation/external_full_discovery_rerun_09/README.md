# EXTERNAL-FULL-DISCOVERY-RERUN-09

Task: `EXTERNAL-FULL-DISCOVERY-RERUN-09`

This handoff starts external full discovery after:

```text
SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-08
HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08
```

Rerun 08 was terminal/current red for commit
`7db32002d7c6ad16a8fb41967d4e43a2ed4bcc5b`. The focused historical validator
repair commit stales that evidence and requires a new external full-discovery
run.

Run id:

```text
source_snapshot_full_discovery_rerun_09
```

Output root:

```text
../eureka-test-runs/source_snapshot_full_discovery_rerun_09
```

Resume with:

```text
SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-09
```

