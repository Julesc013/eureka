# Post-Sync Validation

## Passing Commands

- `py -3 -m py_compile .aide/scripts/aide_lite.py`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py intent validate`
- `py -3 .aide/scripts/aide_lite.py repo inventory`
- `py -3 .aide/scripts/aide_lite.py quality ledger`
- `py -3 .aide/scripts/aide_lite.py quality validate`
- `py -3 .aide/scripts/aide_lite.py refactor validate`
- `py -3 .aide/scripts/aide_lite.py roots validate`
- `py -3 .aide/scripts/aide_lite.py tools validate`
- `py -3 .aide/scripts/aide_lite.py install validate`
- `py -3 .aide/scripts/aide_lite.py repair validate`
- `py -3 .aide/scripts/aide_lite.py upgrade validate`
- `py -3 .aide/scripts/aide_lite.py rollback validate`
- `py -3 .aide/scripts/aide_lite.py uninstall validate`
- `py -3 .aide/scripts/aide_lite.py changelog validate`
- `py -3 .aide/scripts/aide_lite.py github advisory`
- `py -3 .aide/scripts/aide_lite.py github validate`
- `py -3 .aide/scripts/aide_lite.py adapter validate`
- `py -3 scripts/check_architecture_boundaries.py`
- `git diff --check`
- `git check-ignore .aide.local/`

## Warnings / Expected Non-Blockers

- `repo validate`: WARN only; 5891 unknown file classifications remain for Q56/Q57 inventory refinement.
- `verify`: WARN only; the Q56 task packet is narrower than the completed Q55 upgrade diff, and pre-existing native `obj/` is still untracked.
- `eval run`: abnormal exit `-1` after about 258 seconds with no captured output. Critical target and tool-absorption golden tasks were run individually and passed.
- `release status`, `release validate`, `release draft`, and `release draft-validate`: fail in target because Eureka intentionally does not contain `.aide/release/dist/` release artifacts. Source bundle validation passed from the external AIDE dist.

## Boundary / Mutation Result

- No branch mutation.
- No push, fetch, merge, rebase, tag, or GitHub API mutation.
- No provider/model calls.
- No live probes, crawlers, downloaders, source-cache writes, evidence-ledger writes, public-index writes, site deploys, or release publishing.
