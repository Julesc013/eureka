# Validation Report

Focused portable validation run:

```powershell
python -m unittest tests.scripts.test_eureka_portable_cli tests.runtime.test_portable_eureka_instance tests.e2e.test_portable_eureka_instance tests.e2e.test_portable_eureka_clean_machine -v
```

Result:

```text
Ran 15 tests
OK
```

Additional guardrails are run during task closeout. Full unittest discovery is not run inside this task.

Closeout validation:

```text
portable tests: PASS, 15 tests
local instance compatibility: PASS, 30 tests
E2E core: PASS, 30 tests
test-lane focused selector tests: PASS, 6 tests
architecture boundaries: PASS
runtime architecture leakage: valid
public alpha read-only: valid
snapshot relay: pass
test lane policy: valid
git diff --check: PASS
```

`check_generated_artifact_cleanliness.py --check --json` initially reported the new tracked audit packet as generated drift while uncommitted. It is expected to pass after the intentional audit packet is staged/committed.
