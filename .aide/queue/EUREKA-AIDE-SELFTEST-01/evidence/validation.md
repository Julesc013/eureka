# Validation

Interpreter used: `py -3` with Python 3.11.

## Starting State

- `git status --short`: PASS, clean.
- `git branch --show-current`: PASS, `main`.
- `git rev-parse HEAD`: PASS,
  `a8eba4d9d2669ca9b6e78e30cd90c3afa63087bf`.
- `git check-ignore .aide.local/`: PASS, `.aide.local/`.

## Baseline Commands Before Editing

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: FAIL with
  `NameError: name 'core' is not defined` while importing temp fixture
  `core.gateway.__init__`.
- `py -3 .aide/scripts/aide_lite.py selftest`: FAIL with the same temp fixture
  import error.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 4 warnings, 0 errors.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 6/6.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.
- `py -3 scripts/check_architecture_boundaries.py`: PASS, 479 Python files
  checked with no architecture-boundary violations.

## Focused Post-Repair Tests

- `py -3 -m unittest discover -s .aide/scripts/tests -p test_aide_lite.py`:
  PASS, 18 tests.
- `py -3 -m unittest discover -s .aide/scripts/tests -p test_gateway_commands.py`:
  PASS, 6 tests.
- `py -3 -m unittest discover -s .aide/scripts/tests -p test_provider_adapter.py`:
  PASS, 9 tests.
- `py -3 -m unittest discover -s .aide/scripts/tests`: FAIL in unrelated
  export/import fixture coverage that expects full source-pack import fixtures
  such as `.aide/import/import-policy.yaml`; recorded as out of scope for this
  portable selftest fallback repair.

## AIDE Lite Post-Repair Commands

- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 3 warnings, 0 errors before
  packet regeneration; after next-task packet regeneration, WARN with 0 errors
  and warnings limited to future handoff refs, optional imported report refs,
  and temporary diff-scope warnings while evidence files were still uncommitted.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 6/6.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.

## Packet And Report Regeneration

- `py -3 .aide/scripts/aide_lite.py snapshot`: PASS; wrote
  `.aide/context/repo-snapshot.json`, 4,242 files.
- `py -3 .aide/scripts/aide_lite.py index`: PASS; wrote repo map artifacts,
  4,242 files and 2,546 test mappings.
- `py -3 .aide/scripts/aide_lite.py context`: PASS; wrote
  `.aide/context/latest-context-packet.md`, 1,828 chars / 457 approximate
  tokens.
- `py -3 .aide/scripts/aide_lite.py pack --task "Select the next bounded Eureka task after AIDE Lite selftest repair"`:
  PASS; generated a base packet at 3,766 chars / 942 approximate tokens.
- Curated `.aide/context/latest-task-packet.md` to the reviewed
  `EUREKA-AIDE-GOLDEN-01 - Add Eureka-specific AIDE golden tasks` handoff.
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`:
  PASS; 4,598 chars / 1,150 approximate tokens.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS with verifier WARN;
  wrote `.aide/context/latest-review-packet.md`, 4,831 chars / 1,208
  approximate tokens.
- `py -3 .aide/scripts/aide_lite.py ledger scan`: PASS; wrote 15 ledger
  records; one budget warning for the cache report near its configured warning
  threshold.
- `py -3 .aide/scripts/aide_lite.py ledger report`: PASS; 15 records, one
  budget warning, no regression warnings.
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS; 6 active golden tasks.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS; 6/6, no provider/model
  calls, no network calls, no raw prompt/response storage.

## Boundary And Secret Checks

- `py -3 scripts/check_architecture_boundaries.py`: PASS, 479 Python files
  checked with no architecture-boundary violations.
- Strict credential scan with the requested provider-key/private-key pattern:
  PASS after inspection. Matches were false positives from `task-packet` path
  text and literal policy/test marker strings in AIDE Lite code; no actual
  provider key, environment assignment, or private key block was present.

## Final Checks

- `git status --short`: PASS; only scoped `.aide/**` repair, evidence, memory,
  and generated artifacts were modified.
- `git diff --check`: PASS; line-ending normalization warnings only.
- `git check-ignore .aide.local/`: PASS, `.aide.local/`.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 13 warnings, 0 errors
  before final evidence commit. Warnings were future
  `.aide/queue/EUREKA-AIDE-GOLDEN-01/` reference, optional imported
  controller/gateway/provider report references, and active-packet diff-scope
  warnings caused by committing EUREKA-AIDE-SELFTEST-01 evidence while the
  latest task packet already points at the next task.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 6/6.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.
- `py -3 scripts/check_architecture_boundaries.py`: PASS, 479 Python files
  checked with no architecture-boundary violations.
- `py -3 .aide/scripts/aide_lite.py pack --task "Select the next bounded Eureka task after AIDE Lite selftest repair"`:
  PASS; rerun before final report, then the packet was curated back to the
  reviewed `EUREKA-AIDE-GOLDEN-01` handoff.
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`:
  PASS, 4,598 chars / 1,150 approximate tokens.
