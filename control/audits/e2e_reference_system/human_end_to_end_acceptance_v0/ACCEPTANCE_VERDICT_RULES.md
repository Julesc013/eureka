# Acceptance Verdict Rules

Automation must not choose or override the operator verdict.

## PASS

Use when:

- no P0 or P1 issues remain;
- no truth, public, privacy, or boundary concern is unresolved;
- bootstrap, search, Hunt, replay, comparison, and status are coherent;
- status versus authority is understandable;
- core flow is usable without developer explanation;
- the operator accepts the direction.

## PASS_WITH_FIXES

Use when:

- no P0 issue exists;
- no unresolved truth, public, or privacy boundary concern exists;
- the product is coherent enough to continue;
- limited P1/P2 fixes are identified;
- the operator accepts the product direction.

## BLOCKED

Use when:

- core flow cannot be completed;
- server, instance, Hunt, replay, or comparison is broken;
- terminology or interaction prevents evaluation;
- acceptance cannot be concluded.

## FAIL

Use when:

- public/private boundary is violated;
- truth or synthetic status is misrepresented;
- unauthorized mutation occurs;
- private paths, secrets, or tokens leak;
- unsafe action is unexpectedly enabled;
- product direction is rejected by the operator.

## Fix Posture

Do not implement fixes inside the feedback-ingest step. If fixes are needed, propose a scoped follow-up task such as `E2E-HUMAN-ACCEPTANCE-FIXES-01`.
