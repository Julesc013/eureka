# Validation

Initial validation:

- `git branch --show-current`: `dev`
- `git status --short --branch`: clean, tracking `origin/dev`
- `git fetch origin main dev`: pass
- `git rev-parse HEAD`: `ff48400782cec98bf0a8e3c8945cb743378c3e3f`
- `git rev-parse origin/dev`: `ff48400782cec98bf0a8e3c8945cb743378c3e3f`
- `git rev-list --left-right --count origin/dev...HEAD`: `0 0`
- `python .aide/scripts/aide_lite.py commit check --latest`: fail, `ops` type is not allowed
- New fixup commit message: planned as `chore(local): classify instance layout fixup`
- Post-commit generated artifact cleanliness: pass
- Post-commit AIDE latest commit check: pass
- Push: not performed because two instance-layout-caused clean-machine failures remain outside this task's allowed repair paths

Targeted failure rerun:

- 134 tests run
- 12 failures reproduced
- 21 original full-suite failures classified

No operator instance was moved or deleted. No source probes, extraction, model
provider calls, deployment, production readiness claim, or public launch claim
occurred.
