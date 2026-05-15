# Validation

LOCAL-14 validation closed as pass_with_warnings while the pre-existing runtime leakage gate remains disposed.

- JSON parsing: pass for LOCAL-14 inventories and report.
- closeout audit: pass_with_warnings.
- handoff and promotion scripts: pass_with_warnings.
- capability summary generation: pass.
- LOCAL-14 validator: pass_with_warnings.
- focused tests: pass.
- generated artifact cleanliness: fails before commit only because the LOCAL-14 audit pack is untracked; expected to pass after commit.
- architecture boundaries: pass.
- runtime leakage: fail on pre-existing 1030 findings; LOCAL-14 did not increase leakage.
- full discovery: fail_other with historical discovery-lane output and leakage findings.
- old LOCAL validators: rerun by the LOCAL-14 validator; older queue-pointer assertions are recorded as warnings after queue handoff to HUNT-00.
