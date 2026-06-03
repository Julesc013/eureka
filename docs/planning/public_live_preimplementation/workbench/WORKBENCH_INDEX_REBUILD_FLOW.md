# Workbench Index Rebuild Flow

```text
review event
-> reviewed record delta
-> rebuild plan
-> dry-run validation
-> operator approval if required
-> index rebuild
-> snapshot/public projection refresh
-> rollback evidence
```

Index rebuild must preserve:

- before/after manifest
- record delta
- validation result
- rollback path
- public visibility posture

Fallback candidates do not enter reviewed indexes until review promotion.

