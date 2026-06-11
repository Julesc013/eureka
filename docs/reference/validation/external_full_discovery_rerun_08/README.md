# EXTERNAL-FULL-DISCOVERY-RERUN-08

Task: `EXTERNAL-FULL-DISCOVERY-RERUN-08`

This handoff starts external full discovery after:

```text
SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-07
IA-METADATA-PROVIDER-WIRING-AUTHORIZATION-00
IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00
```

Rerun 07 was green for commit `946b782a6b158157087910bd5653c0fed4261925`, but
the ingest, queue authorization, and IA metadata provider smoke commits stale that evidence.

Run id:

```text
source_snapshot_full_discovery_rerun_08
```

Output root:

```text
../eureka-test-runs/source_snapshot_full_discovery_rerun_08
```

Resume with:

```text
SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-08
```

