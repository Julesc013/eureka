# Validation Report

Planned authorization validation:

```text
git diff --check
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
py -3 .aide/scripts/aide_lite.py commit check --latest
```

Result: `PASS`

Additional authorization checks:

```text
py -3 .aide/scripts/aide_lite.py pack --task "IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00"
py -3 .aide/scripts/aide_lite.py task status
```

Result:

```text
current_recommended_task: IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00 - Bounded IA metadata provider smoke; external artifact evidence and hardware details remain waiting
```
