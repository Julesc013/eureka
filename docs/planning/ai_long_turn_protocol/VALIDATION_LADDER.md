# Validation Ladder

Use the lowest lane that honestly fits the change, then add focused checks when
the diff touches riskier boundaries. Report actual commands and results only.

## Tier 0: Always

```powershell
git status --short
git diff --check
```

Use this for basic worktree and whitespace validation.

## Tier 1: AIDE Operating Baseline

```powershell
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
```

For substantive work, also run:

```powershell
py -3 .aide/scripts/aide_lite.py pack --task "<bounded task>"
```

If `pack` rewrites generated context, include or report that artifact
deliberately. Do not hide generated context drift.

## Tier 2: Repo Boundary And Generated Artifact Guards

```powershell
python scripts/check_architecture_boundaries.py
python scripts/check_generated_artifact_cleanliness.py --check --json
```

Run architecture boundaries when Python layering, runtime, gateway, connector,
surface, or import ownership could be affected. For docs-only protocol work it
is still a useful low-cost guard.

## Tier 3: Changed And Failed-First Selection

```powershell
py -3 scripts/eureka_test_select.py --changed --failed-first --json
```

Run focused tests recommended by the selector. If the selector reports no
focused lane for a docs-only change, record that result.

## Tier 4: Task-Specific Focused Tests

Use task-local validators or tests named by:

- `docs/operations/TEST_AND_EVAL_LANES.md`;
- `control/inventory/tests/command_matrix.json`;
- the task README, validation report, or handoff;
- the changed scripts, tests, contracts, or runtime modules.

Do not weaken tests, fixtures, or expected evidence to make a lane pass.

## Tier 5: External Full Discovery

Full unittest discovery is not a normal AI-session command. If required, create
or use an external handoff and stop with:

```text
WAITING_FOR_EXTERNAL_FULL_DISCOVERY
```

The operator or CI returns compact artifacts such as
`full_unittest_summary.json`, `failure_families.json`, and `failed_tests.txt`.
Do not paste raw logs into the AI session.

## Reporting Rule

Separate:

- `Tests run`: actual commands and results;
- `Expected tests`: checks that should be green later or externally;
- `Not run`: checks intentionally skipped with the reason.

Never imply full validation if only a focused lane ran.
