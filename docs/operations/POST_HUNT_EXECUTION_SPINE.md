# Post-HUNT Execution Spine

After HUNT closeout, new hard searches should move through the local
investigation spine:

```text
reviewed local index -> Search Hunt -> exhaustion -> SearchNeed -> WorkUnit
```

Only safe deterministic local WorkUnits may run under current policy. Source
probes, extraction, AI providers, downloads, install actions, source sync, and
deployment remain disabled until future reviewed gates enable a narrow action.

Completed WorkUnits and AI candidate outputs are not truth. Evidence acceptance,
rights, safety, source approval, and index mutation still require their
respective review paths.
