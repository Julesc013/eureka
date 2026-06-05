# Full Discovery Summary Digest

## Summary

| Field | Value |
|---|---:|
| Tests run | 5505 |
| Failures | 45 |
| Errors | 1 |
| Skipped | 0 |
| Exit code | 1 |
| Duration seconds | 2938.81957 |

## Command

```text
python -m unittest discover -s tests -t .
```

## Result

```text
FAILED (failures=45, errors=1)
```

## Failed Modules

The summary reports failures across operations validators, runtime source
observation validation, repo-structure validation, promotion validators, and
TSIS validation. The largest failure cluster is stale queue/task-state
expectations across older HUNT, LOCAL, and promotion tracks.

## Evidence Limits

The external summary proves current full-discovery state for this commit. It
does not prove product readiness, artifact verification, public-alpha
readiness, or launch approval.
