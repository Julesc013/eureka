# Validation

Interpreter used: `py -3` with Python 3.11.

## Baseline Before Editing

- `git status --short`: PASS, clean.
- `git branch --show-current`: PASS, `main`.
- `git rev-parse HEAD`: PASS,
  `8cf62926f7aade64edc6e1680ab5550cd8c9fff1`.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.

## Final Validation

- `py -3 .aide/scripts/aide_lite.py snapshot`: PASS; wrote
  `.aide/context/repo-snapshot.json`, 4,274 files.
- `py -3 .aide/scripts/aide_lite.py index`: PASS; wrote repo map, test map,
  and context index; 2,577 test mappings.
- `py -3 .aide/scripts/aide_lite.py context`: PASS; latest context packet is
  1,828 chars / 457 approximate tokens.
- `py -3 .aide/scripts/aide_lite.py pack --task "EUREKA-AIDE-REAL-01 Add Eureka AIDE Lite repo-health report"`:
  PASS; generated a base packet, then the packet was curated to include final
  handoff refs.
- `py -3 .aide/scripts/aide_lite.py estimate --file .aide/context/latest-task-packet.md`:
  PASS; 4,231 chars / 1,058 approximate tokens.
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS, 12/12; no
  provider/model/network calls and no raw prompt/response storage.
- `py -3 .aide/scripts/aide_lite.py route explain`: PASS; advisory route
  emitted with no provider/model/network calls.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS; latest review packet
  is 5,440 chars / 1,360 approximate tokens with verifier WARN.
- `py -3 .aide/scripts/aide_lite.py ledger scan`: PASS; 15 records, one
  near-budget cache-report warning, no regression warnings.
- `git status --short`: PASS; only scoped AIDE handoff, AGENTS guidance, and
  generated AIDE artifacts were modified before commit.
- `git diff --check`: PASS; line-ending normalization warnings only.
- `git check-ignore .aide.local/`: PASS, `.aide.local/`.
- `py -3 scripts/check_architecture_boundaries.py`: PASS, 479 Python files
  checked with no architecture-boundary violations.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS, 12 active tasks.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, 14 warnings, 0 errors.
  Warnings were future `EUREKA-AIDE-REAL-01` queue references, optional
  imported controller/gateway/provider report references, and active-packet
  diff-scope warnings while final handoff evidence was still uncommitted.
- Strict credential scan: PASS after inspection. Matches were false positives
  from `task-packet` path text and literal policy/test marker strings; no
  actual provider key, environment assignment, or private-key block was found.
