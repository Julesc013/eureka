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

## Executable Runner

Archive Resolution Eval Runner v0 now executes this packet through the bounded
Python reference lane:

1. load and validate the task fixtures
2. run Query Planner v0
3. build/use Local Index v0 once per suite when available
4. fall back to deterministic search when needed
5. call bounded absence reasoning for empty results
6. emit stable JSON task and suite results

The expected planner fields now exercise Old-Platform Software Planner Pack v0
for deterministic old-platform interpretation: Windows aliases are platform
constraints, latest-compatible release queries carry a temporal goal, vague
identity queries preserve uncertainty, and member/document queries carry
bounded representation or decomposition hints. These expectations do not make
the hard tasks pass; they only guard planner interpretation.

Run it with:

```powershell
python scripts/run_archive_resolution_evals.py
python scripts/run_archive_resolution_evals.py --json
python scripts/run_archive_resolution_evals.py --task windows_7_apps
```

The runner must not make the hard fixtures look solved. Many current tasks are
reported as `capability_gap` because the bounded corpus does not yet contain the
direct artifacts, member paths, article boundaries, or evidence needed for full
satisfaction. This is intentional. The runner is not a ranking benchmark, not a
semantic/fuzzy/vector benchmark, and not a production relevance evaluation.

Hard Eval Satisfaction Pack v0 records that archive-resolution evals moved to
`capability_gap=1` and `partial=5` by mapping existing source-backed member,
representation, compatibility, and source-family evidence into hard
expected-result checks.

Old-Platform Result Refinement Pack v0 then added deterministic
`result_shape.primary_candidate`, `lanes.expected_lanes`, and
`ranking.bad_result_patterns` checks for those source-backed partials. Current
archive-resolution evals now report `capability_gap=1`, `partial=4`, and
`satisfied=1`: `driver_inside_support_cd` is satisfied because the primary
candidate is a source-backed driver member, while the Firefox, FTP, Windows 98
registry repair, and Windows 7 app tasks remain partial with explicit
result-shape or evidence limits. The article-inside-scan task remains a true
capability gap because no bounded article/page/OCR fixture exists.
