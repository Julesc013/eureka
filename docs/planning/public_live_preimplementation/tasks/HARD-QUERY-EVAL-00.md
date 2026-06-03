# HARD-QUERY-EVAL-00

Goal: run and report hard-query usefulness before launch.

Inputs to read first: `evals/*.md`, `evals/HARD_QUERY_SET_V0.yml`,
existing `evals/archive_resolution/**` and `evals/search_usefulness/**`.

Allowed paths: evals, tests/evals, runtime eval runner if needed, control
reports.

Protected paths: reviewed/public indexes unless explicitly part of a reviewed
gate.

Deliverables: eval run, scorecard, failures converted to needs/near misses/
blocked states/tasks.

Non-goals: public launch, source crawling, truth promotion.

Validation: eval loader/runner tests and focused eval commands.

Exit criteria: usefulness is measured before launch.

Impact statement: eval/control impact.

