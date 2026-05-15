# LOCAL To Main Promotion Review

LOCAL-14 does not merge dev to main and does not push branches.

Promotion requires a separate `LOCAL-TO-MAIN-PROMOTION-REVIEW` task. That review
must inspect branch state, closeout evidence, warning disposition, leakage
status, generated artifact cleanliness, and no-claim boundaries before any
branch mutation.

Because the runtime leakage warning remains unresolved, automatic main
promotion is not recommended by LOCAL-14.
