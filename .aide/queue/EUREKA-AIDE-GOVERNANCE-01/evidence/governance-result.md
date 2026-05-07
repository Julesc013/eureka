# Governance Result

This task adds two AIDE operating gates for future Eureka work.

## Commit Messages

AIDE now documents and checks changelog-ready commit messages:

- first line follows `type(scope): summary`;
- body uses stable Markdown headings;
- validation records PASS/WARN/FAIL/NOT RUN;
- changelog bullets use machine-readable category prefixes;
- a checker command and optional hook template are available.

This matches the practical industry baseline of Conventional Commits while
adding stricter Markdown body sections for automated changelog and release-note
generation.

## Task Resumption

AIDE now documents and checks that tasks are reusable and resumable:

- stable task ids and queue/status/evidence surfaces are required;
- repeated prompts resume from evidence or advance when already complete;
- out-of-order prompts are reconciled against queue state and prerequisites;
- incomplete prior work is inspected and continued or closed when safe;
- user escalation happens only after repo-local evidence is insufficient.

## Enforcement Surface

- `py -3 .aide/scripts/aide_lite.py commit check --message-file <path>`
- `py -3 .aide/scripts/aide_lite.py commit check --latest`
- `py -3 .aide/scripts/aide_lite.py eval run --task commit_message_standard_golden`
- `py -3 .aide/scripts/aide_lite.py eval run --task task_resumption_standard_golden`
