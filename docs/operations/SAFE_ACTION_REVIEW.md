# Safe Action Review

J0 action outputs are review-gated. They can be used as local evidence for future review but are not review decisions.

Reviewers should confirm:

- the action family is safe or explicitly blocked
- no output claims download, mirror, install, execution, or emulation
- no evidence, candidate, source, pack, public truth, public index, or master index mutation is accepted
- limitations and safe alternatives are present

Use `python scripts/validate_safe_actions_runtime.py` before treating J0 artifacts as ready.
