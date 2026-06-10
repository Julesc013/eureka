# External Discovery Policy

Full unittest discovery and other long validation lanes are external/manual
gates for AI-assisted work. They are not background chat tasks.

## When Full Discovery Is Required

Require external full discovery for:

- promotion or pre-main merge gates;
- public-alpha closeout or launch readiness gates;
- broad runtime, surface, connector, or contract changes where focused tests
  cannot localize risk;
- stale full-discovery evidence after meaningful commits;
- a task packet that explicitly asks for full discovery.

## AI-Session Behavior

Inside the AI session:

- do not run `python -m unittest discover -s tests -t .`;
- do not stream repeated progress updates while a long command runs;
- do not read raw stdout/stderr unless a compact summary is insufficient and a
  targeted traceback excerpt is needed;
- do not claim a full-discovery pass from old or mismatched HEAD evidence.

## Handoff Shape

A handoff should name:

```text
run_id:
repo:
branch:
expected_head:
command:
output_root:
required_return_artifacts:
resume_task:
stop_status: WAITING_FOR_EXTERNAL_FULL_DISCOVERY
```

Default output root should be outside the repo, usually under:

```text
../eureka-test-runs/<run-id>
```

## Required Return Artifacts

Ask for compact artifacts:

- `status.json`, if the harness writes one;
- `full_unittest_summary.json`;
- `failure_families.json`;
- `failed_tests.txt`;
- `git status --short --branch`;
- `git rev-parse HEAD`.

Do not ask the operator to paste raw logs unless the summary does not identify
the failing family.

## Resume Rule

Resume only when the returned artifacts match the expected branch and HEAD, or
when the mismatch is explicitly accepted as stale evidence. Stale evidence may
support risk analysis; it does not support launch, promotion, or readiness
claims.
