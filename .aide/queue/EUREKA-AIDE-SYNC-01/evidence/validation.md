# Q32 Validation

## Baseline Before Sync

- `git status --short`: PASS, clean.
- `git branch --show-current`: PASS, `dev`.
- `git branch --all`: PASS, local `dev`, `main`; remotes `origin/dev`,
  `origin/main`, `origin/HEAD -> origin/main`.
- `git remote -v`: PASS, origin `https://github.com/Julesc013/eureka.git`.
- `git rev-parse HEAD`: PASS,
  `cf0c53a41d9374b3758fe1c12b08f4a7a50c54b8`.
- `git check-ignore .aide.local/`: PASS, `.aide.local/`.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 14/14 golden tasks.
- `py -3 .aide/scripts/aide_lite.py verify`: PASS.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS.
- `py -3 .aide/scripts/aide_lite.py changelog preview`: NOT AVAILABLE in
  pre-sync Eureka AIDE Lite, command exited 2.
- `py -3 .aide/scripts/aide_lite.py git detect|doctor|status|policy|plan`:
  NOT AVAILABLE in pre-sync Eureka AIDE Lite, each command exited 2.
- `py -3 scripts/check_architecture_boundaries.py`: PASS, 632 Python files,
  no architecture-boundary violations.

## Final Validation

- `git status --short`: PASS before evidence finalization; final evidence
  commit follows this validation.
- `git diff --check`: PASS.
- `git branch --show-current`: PASS, `dev`.
- `git branch --all`: PASS, local `dev`, `main`; remotes `origin/dev`,
  `origin/main`, `origin/HEAD -> origin/main`.
- `git check-ignore .aide.local/`: PASS, `.aide.local/`.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 31/31 golden tasks.
- `py -3 .aide/scripts/aide_lite.py verify --write-report .aide/verification/latest-verification-report.md`:
  PASS, 0 warnings, 0 errors.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS; verifier result PASS,
  review packet within budget.
- `py -3 .aide/scripts/aide_lite.py ledger scan`: PASS with budget warnings
  for generated eval reports and cache report only.
- `py -3 .aide/scripts/aide_lite.py ledger report`: PASS with the same budget
  warnings; no token regression warnings.
- `py -3 .aide/scripts/aide_lite.py commit check --latest`: PASS for the
  latest structured commit before evidence finalization.
- `py -3 .aide/scripts/aide_lite.py commit template`: PASS.
- `py -3 .aide/scripts/aide_lite.py changelog preview`: WARN because 15 older
  commits in the preview range predate the structured policy. New Q32 commits
  are structured.
- `py -3 .aide/scripts/aide_lite.py task inspect --task-id EUREKA-AIDE-SYNC-01`:
  PASS after status finalization; classification complete with
  `noop_already_complete` recovery suggestion.
- `py -3 .aide/scripts/aide_lite.py task status`: PASS.
- `py -3 .aide/scripts/aide_lite.py task noop-check --task-id EUREKA-AIDE-SYNC-01`:
  PASS after status finalization; result `noop_already_complete`.
- `py -3 .aide/scripts/aide_lite.py git detect`: PASS; workflow
  `trunk_with_dev_integration`, current branch `dev`, role `integration`.
- `py -3 .aide/scripts/aide_lite.py git doctor`: PASS with dirty-tree warning
  while final evidence changes are present; non-mutating.
- `py -3 .aide/scripts/aide_lite.py git status`: PASS with dirty-tree warning;
  non-mutating.
- `py -3 .aide/scripts/aide_lite.py git policy`: PASS.
- `py -3 .aide/scripts/aide_lite.py git plan`: PASS/blocked as expected by
  dirty-tree safety gate; non-mutating.
- `py -3 .aide/scripts/aide_lite.py git sync --dry-run`: PASS/blocked by dirty
  tree; no fetch, pull, push, merge, prune, or branch mutation performed.
- `py -3 .aide/scripts/aide_lite.py git land --dry-run --target dev`:
  PASS/blocked because current branch is `dev` integration, not a task branch;
  no mutation.
- `py -3 .aide/scripts/aide_lite.py git promote --dry-run --from dev --to main`:
  PASS/blocked by dirty tree; no mutation.
- `py -3 .aide/scripts/aide_lite.py git prune --dry-run`: PASS; protected
  `main` and current `dev` are not eligible.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py pack --task "Select the next bounded Eureka task after canonical AIDE governance sync"`:
  PASS; packet then received target-specific boundary refs required by Eureka
  golden checks.
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`:
  PASS, 4133 chars / 1034 approx tokens.
- `py -3 scripts/check_architecture_boundaries.py`: PASS, 632 Python files, no
  violations.
- Targeted secret scan: PASS after inspection. Matches are policy/test/path
  text such as `task-packet`, `TOKEN_ESTIMATE`, example `api_key` strings, and
  existing secret-policy documents; no actual provider key, private-key block,
  raw prompt, or raw response was found.

## Notes

- No branch helper `--apply` or `--push` command was run.
- No AIDE source repo, Dominium repo, product source path, provider/model
  command, network call, or GitHub API mutation was performed.
