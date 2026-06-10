# Source Snapshot Full Discovery Ingest 05

Task: `SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-05`

This reference pack ingests the terminal external full-discovery rerun:

```text
source_snapshot_full_discovery_rerun_05
```

The run is current to `dev` HEAD:

```text
9200df49f084cf313cccf821bf56f0194376f202
```

Result:

```text
status: fail
tests_run: 5643
failures: 39
errors: 0
skipped: 0
duration_seconds: 2866.304682
```

The failure evidence is compact external validation evidence. This ingest does
not run full discovery inside the AI session, repair failures, launch public
alpha, promote `dev -> main`, mutate runtime/product behavior, create reviewed
artifact records, or create verified artifact claims.

