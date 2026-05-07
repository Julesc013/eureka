# Source Comment Standard

Future comments and docstrings should explain why, invariants, assumptions,
side effects, recovery behavior, and failure modes. Code and function names
should carry the obvious what.

## When To Comment

- Nontrivial scripts should have a file/module docstring.
- Public helpers and validators should have function docstrings.
- Inline comments should explain non-obvious policy decisions.
- Safety boundaries and forbidden behavior should be explicit.
- Idempotency and recovery behavior should be documented near the logic.
- Legacy/native/old-toolchain quirks deserve explanatory comments.
- Privacy, security, rights, and risk-sensitive checks need failure-mode notes.

## Advisory Density

The density bands in `.aide/policies/source-comment-policy.yaml` are advisory at
this milestone. Existing code must not hard-fail because it lacks comment
density. Future validators may report density as advisory evidence.

## Anti-Patterns

Avoid comments that restate syntax, duplicate large docs, explain obvious
variable names, or leave stale TODOs without an owner or next step.
