# SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-08

Task: `SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-08`

This package ingests terminal external full-discovery rerun 08.

Run id:

```text
source_snapshot_full_discovery_rerun_08
```

Result:

```text
status: fail
tests_run: 5676
failures: 23
errors: 0
current_to_head: true
```

Rerun 08 is current to `dev` commit
`7db32002d7c6ad16a8fb41967d4e43a2ed4bcc5b`.

The failures classify as historical validator/queue expectation drift, not as
IA metadata provider behavior failure.

Next task:

```text
HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08
```

