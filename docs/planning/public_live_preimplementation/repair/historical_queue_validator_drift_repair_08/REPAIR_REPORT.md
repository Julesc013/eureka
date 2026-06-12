# Repair Report

## Status

`PASS_WITH_EXTERNAL_RERUN_REQUIRED`

## Input

External full discovery rerun 08 was terminal/current when ingested at
`7db32002d7c6ad16a8fb41967d4e43a2ed4bcc5b`.

```text
run_id: source_snapshot_full_discovery_rerun_08
tests_run: 5676
failures: 23
errors: 0
```

## Repair

Updated historical validator successor checks so completed HUNT, public-alpha
defer, and dev-to-main promotion validation tasks accept the current later
governed product-proof and validation chain:

```text
IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00
HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08
EXTERNAL-FULL-DISCOVERY-RERUN-09
SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-09
WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE
WAITING_FOR_USER_HARDWARE_DETAILS
```

The repair also tightens stale allowlists so they do not treat the following as
valid blocked successors without their dedicated gates:

```text
PUBLIC-ALPHA-LAUNCH-00
PUBLIC-ALPHA-READINESS-00
DEV-TO-MAIN-PROMOTION-REVIEW-*
```

## Boundaries

```text
runtime changed: no
contracts changed: no
surface behavior changed: no
IA provider behavior changed: no
queue rewound: no
public alpha launched: no
dev -> main promoted: no
artifact evidence invented: no
reviewed/public/master indexes mutated: no
```

## Result

Focused rerun-08 failed modules pass after the repair.

Full discovery must be rerun externally because the repair changes validators
and tests.

