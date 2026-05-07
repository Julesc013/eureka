# Eureka Commit Message Standard

This is the repo-local AIDE standard for future Eureka commits. It uses the
industry-standard Conventional Commits subject line, then adds a structured
Markdown body so commits can become automated changelog and release-note input.

## Subject

Use:

```text
type(scope): summary
```

Rules:

- Keep the subject at 72 characters or fewer.
- Use a concrete outcome, not a vague activity.
- Avoid placeholders such as `update`, `misc`, `wip`, or `fix`.
- Do not end the subject with a period.
- Prefer scopes such as `aide`, `contracts`, `runtime`, `docs`, `tests`,
  `queue`, or the task id when that is clearer.

Good:

```text
docs(aide): add convergence audit for Track A handoff
```

Weak:

```text
update docs
```

## Body

Every substantive AIDE-managed commit should include these Markdown sections:

```markdown
## Summary

- One or two bullets explaining the outcome.

## Changed

- Paths or behavior surfaces changed.

## Validation

- `command`: PASS/WARN/FAIL/NOT RUN, with the important note.

## Changelog

- Added: user-facing or operator-facing additions.
- Changed: behavior, docs, queue, policy, or validation changes.
- Fixed: bug fixes.
- Removed: removals.
- Docs: documentation-only changes.
- Tests: tests or deterministic gates.
- Internal: repo-operating metadata and maintenance changes.

## Risks

- Known warnings, deferred work, or why risk is low.

## Follow-up

- Next task, review gate, or `None`.
```

## Enforcement

AIDE checks this format with:

```text
py -3 .aide/scripts/aide_lite.py commit check --message-file <path>
py -3 .aide/scripts/aide_lite.py commit check --latest
py -3 .aide/scripts/aide_lite.py eval run --task commit_message_standard_golden
```

The committed hook template at `.aide/hooks/commit-msg` can be copied or linked
into a local Git hook setup by an operator. The template is not automatically
installed because local hook paths are machine-local state.
