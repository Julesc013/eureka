# Archive Resolution Evals

`evals/archive_resolution/` holds a small hard-query benchmark for future
archive-resolution work.

This corpus is intentionally:

- software-first
- repo-level rather than component-local
- draft and bootstrap-scale
- focused on difficult human queries that existing archive search often handles
  poorly

The purpose of this directory is to give future work on investigation runs,
ranking, decomposition, member-level records, source expansion, and optional AI
helpers a governed guardrail before broader search claims are made.

## Layout

- `task.schema.yaml`: draft schema for one benchmark task
- `tasks/`: one task file per query family scenario

## Bootstrap Loader Note

The current executable lane remains Python stdlib-only. To keep this corpus
machine-readable without introducing a YAML dependency, the task files and the
schema file currently use the JSON subset of YAML. They are still stored as
`.yaml` because they are governed draft artifacts intended to evolve with the
rest of Eureka's schema material.

## Current Focus

The initial v0 task set emphasizes cases where Eureka should eventually return
the smallest actionable unit rather than only the outer container or a shallow
metadata hit.
