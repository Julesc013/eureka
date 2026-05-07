# Commit And Changelog Standard

Eureka commits should be understandable from the subject line and useful as
future changelog input. Use:

```text
<type>(<scope>): <concise outcome>
```

Allowed types live in `.aide/policies/commit-message-standard.yaml` and include
`feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `contracts`, `runtime`,
`surface`, `eval`, `audit`, `ops`, `native`, `site`, `aide`, `security`, and
`revert`.

## Required Body

Every substantive future commit should include:

- `## Summary`
- `## Why`
- `## Changed`
- `## Validation`
- `## Changelog`
- `## Risks`
- `## Follow-up`

The `## Why` section is intentional: future agents should understand the
motivation before replaying details.

## Changelog Shape

Use grouped bullets that can be parsed by
`scripts/preview_eureka_changelog.py`:

```text
## Changelog

- Added:
  - New operator-facing behavior or artifacts.
- Tests:
  - New deterministic validation.
- Internal:
  - Repo-operating metadata or evidence.
```

Empty groups may be omitted.

## Required Trailers

```text
AIDE-Task: <id>
AIDE-Result: PASS|PASS_WITH_WARNINGS|PARTIAL|FAIL|BLOCKED
AIDE-Scope: aide|docs|contracts|runtime|surface|site|eval|ops|native|tests|control|mixed
AIDE-Change-Class: added|changed|fixed|removed|deprecated|security|tests|docs|internal|mixed
AIDE-Quality-Gate: pass|warn|fail|not-run
AIDE-WorkUnit: idempotent|resume|noop|blocked|not-applicable
```

`PASS_WITH_WARNINGS` is acceptable when warnings are documented and there are
zero errors.

## Preview

Preview a sample commit message:

```text
python scripts/preview_eureka_changelog.py --message-file examples/commit_messages/valid_structured_commit.txt
```

The preview tool writes to stdout by default and does not mutate `CHANGELOG.md`.
