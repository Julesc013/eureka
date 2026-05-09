# Test Report

The full Python unittest suite was run from `main` after merging SYNC-GUARD-01.

```text
python -m unittest discover -s tests -t .
Ran 2508 tests in 188.453s
OK
```

The SYNC-GUARD targeted tests were also run separately:

```text
python -m unittest tests.operations.test_git_task_state_guard tests.operations.test_sync_guard_policy
Ran 14 tests
OK
```

The guard edge cases covered by targeted tests include:

- clean task branch
- dirty worktree
- active merge marker
- active rebase marker
- active cherry-pick marker
- direct `main` task start
- no-upstream warning
- branch behind upstream
- secret-like untracked path
- JSON output
- policy validator pass
- required docs and prompt files
- forbidden destructive command policy
