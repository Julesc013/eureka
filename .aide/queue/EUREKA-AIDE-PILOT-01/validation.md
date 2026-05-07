# Validation

## Baseline

- `git status --short`: clean before edits.
- `git branch --show-current`: `main`.
- `git rev-parse HEAD`: `4c726f849c39763476fa24b81529c7d0d282c844`.
- Source `pack-status`: PASS; checksums valid; boundary PASS.
- Q21 `import-pack --dry-run`: 127 operations, 0 conflicts, no provider/model/network calls.

## AIDE Lite Commands

- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py snapshot`: PASS; 4220 files; no inline contents.
- `py -3 .aide/scripts/aide_lite.py index`: PASS; 4220 files; 2524 test mappings.
- `py -3 .aide/scripts/aide_lite.py context`: PASS; 1808 chars / 452 approx tokens.
- `py -3 .aide/scripts/aide_lite.py pack --task "Audit Eureka current repo state and produce the next compact implementation task"`: PASS; 3792 chars / 948 approx tokens.
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`: PASS; 3792 chars / 948 approx tokens.
- `py -3 .aide/scripts/aide_lite.py verify --write-report .aide/verification/latest-verification-report.md`: WARN; 6 warnings; 0 errors.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS; 4208 chars / 1052 approx tokens.
- `py -3 .aide/scripts/aide_lite.py ledger scan`: PASS; 15 records; one cache-report near-budget warning.
- `py -3 .aide/scripts/aide_lite.py ledger report`: PASS; 15 records.
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS; 6 golden tasks listed.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS; 6/6 golden tasks passed.
- `py -3 .aide/scripts/aide_lite.py adapter render`: PASS; generated preview outputs under `.aide/generated/adapters/`.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py cache report`: PASS; no raw prompt/response storage.
- `py -3 .aide/scripts/aide_lite.py cache status`: PASS; `.aide.local/` ignored and untracked.
- `py -3 .aide/scripts/aide_lite.py route explain`: PASS; advisory only; no provider/model/network calls.
- `py -3 .aide/scripts/aide_lite.py route validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py outcome report`: WARN; advisory only; no automatic application.

## Expected Failures / Limitations

- `py -3 .aide/scripts/aide_lite.py provider validate`: FAIL because optional `core/providers/**` was not imported under Q22 scope.
- `py -3 .aide/scripts/aide_lite.py gateway smoke`: FAIL because optional `core/gateway/**` was not imported under Q22 scope.
- `py -3 .aide/scripts/aide_lite.py selftest`: FAIL in the imported pack's temporary fixture with `NameError: name 'core' is not defined`.
- `py -3 .aide/scripts/aide_lite.py test`: same selftest fixture failure.

## Git / Safety

- `git diff --check`: PASS.
- `git check-ignore .aide.local/`: PASS.
- Actual `.aide.local/`: not created.
- `python scripts/check_architecture_boundaries.py`: PASS; checked 479 Python files; no boundary violations.
- Targeted broad secret scan: 202 matches, inspected as policy/example/token-discipline text rather than live credentials.
- Targeted strict key scan: PASS; 0 matches for OpenAI/Anthropic/DeepSeek/private-key style credentials.
