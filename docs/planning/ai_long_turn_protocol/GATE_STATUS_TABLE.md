# Gate Status Table

Every connected or long turn should record gate state at the start and at the
end. Refresh from repo-local evidence; do not rely on memory or old prompt
text when current files are available.

## Template

| Gate | Start | End | Evidence | Notes |
|---|---:|---:|---|---|
| branch | `<branch>` | `<branch>` | `git rev-parse --abbrev-ref HEAD` | |
| HEAD | `<hash>` | `<hash>` | `git rev-parse HEAD` | |
| worktree | clean/dirty | clean/dirty | `git status --short --branch` | |
| origin divergence | `<left> <right>` | `<left> <right>` | `git rev-list --left-right --count origin/dev...HEAD` | |
| current queue | `<task/status>` | `<task/status>` | `.aide/queue/index.yaml` | |
| public alpha | blocked/pass | blocked/pass | gate report | |
| `dev -> main` | blocked/pass | blocked/pass | promotion report | |
| source/snapshot release | blocked/pass/stale | blocked/pass/stale | discovery ingest report | |
| reviewed artifact records | `<n>/<threshold>` | `<n>/<threshold>` | artifact gate report | |
| verified artifacts | `<n>` | `<n>` | artifact gate report | |
| external artifact evidence | waiting/returned | waiting/returned | return contract or summary | |
| user hardware details | waiting/satisfied | waiting/satisfied | queue or user-provided details | |

## Creation Snapshot

Observed while creating `AI-LONG-TURN-OPERATING-PROTOCOL-00`:

| Gate | Status | Evidence |
|---|---|---|
| branch | `dev` | `git rev-parse --abbrev-ref HEAD` |
| starting HEAD | `e3d34248ed6fb8d223aba054d6c2f6f96ba2ae84` | `git rev-parse HEAD` |
| origin divergence | `0 12` against `origin/dev...HEAD` | `git rev-list --left-right --count origin/dev...HEAD` |
| worktree | clean before edits | `git status --short --branch` |
| current queue | `WAITING_FOR_EXTERNAL_ARTIFACT_EVIDENCE` | `.aide/queue/index.yaml` |
| secondary blocker | `WAITING_FOR_USER_HARDWARE_DETAILS` | `.aide/queue/index.yaml` |
| reviewed artifact records | 4 of 25 | `docs/reference/artifact_evidence_gap_batch_01/gate_status.md` |
| verified artifacts | 0 | `docs/reference/artifact_evidence_gap_batch_01/gate_status.md` |
| public alpha | blocked | reviewed artifact records below threshold |
| `dev -> main` | blocked | promotion preflight not run and public-alpha gates blocked |

## Update Rule

If a turn changes gate state, cite the file or command that proves it. If the
turn does not change gate state, say that explicitly.
