# Successor Semantics

The repaired validators accept the current Source Foundry successor chain only
through explicit task IDs and prefixes. They do not accept arbitrary future
queue states.

Accepted Source Foundry successor chain:

```text
IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00
IA-SOURCE-OBSERVATION-CACHE-DELTA-00
IA-CANDIDATE-INDEX-REFRESH-00
IA-EVIDENCE-LEDGER-SUMMARY-00
REVIEW-IA-CANDIDATES-BATCH-00
```

Parallel validation lane prefixes accepted for task-packet validation:

```text
SOURCE-FOUNDRY-
HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-
EXTERNAL-FULL-DISCOVERY-
```

Public launch, reviewed-record creation, reviewed/master index mutation, public
index mutation, provider calls, downloads, and production readiness remain
forbidden by the repaired checks.
