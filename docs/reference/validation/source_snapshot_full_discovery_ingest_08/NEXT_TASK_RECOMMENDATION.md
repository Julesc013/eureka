# Next Task Recommendation

Recommended next task:

```text
HISTORICAL-QUEUE-VALIDATOR-DRIFT-REPAIR-08
```

Why:

```text
External full discovery rerun 08 is terminal/current red. The failures are broad historical validator expectation drift across HUNT, public-alpha defer, and dev-to-main promotion validators.
```

Not recommended yet:

```text
LOCAL-METADATA-FALLBACK-E2E-DEMO-00
```

Reason:

```text
The product pivot requires green/current rerun 08 ingest first. Rerun 08 is red.
```

Expected repair scope:

```text
Update historical validator successor/current-task allowlists or disposed-state logic so old queue validators remain truthful after the IA metadata provider smoke successor.
```

Public alpha and `dev -> main` remain blocked.

