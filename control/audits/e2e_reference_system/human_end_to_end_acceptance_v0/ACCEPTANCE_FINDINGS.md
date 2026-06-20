# Acceptance Findings

Status: BLOCKED_BY_FIRST_USE_UX

## Summary

The human acceptance gate worked: it found that Eureka Local Reference System v0 is not self-explanatory on first use.

This is a product UX failure, not an operator mistake.

## Findings

### P1 Blocking

- First-use handoff and product entry experience are confusing before meaningful evaluation can begin.
- The operator could not tell what to do with the product from the supplied handoff and first-run context.
- The handoff exposed too much process/audit framing instead of a simple product action path.

### P2 Significant

- The first-run experience needs a plain-language introduction, obvious search entry point, example searches, and clear result/empty/error/blocked states.
- "Hunt" needs to be explained at the moment it becomes relevant, not through architecture or internal docs.

### P3 Polish

- Future human handoff should be limited to four product-facing steps.

### Future Enhancements

- Full product acceptance can resume after the first-run UX repair and automated clean-start browser smoke test.

## Not Observed

- No public exposure issue was reported.
- No truth-boundary issue was reported.
- No reviewed-record creation was reported.
- No index mutation was reported.
- No provider/network/download issue was reported.

## Required Repair

Next task: `EUREKA-FIRST-RUN-ACCEPTANCE-UX-00`

Required deliverables:

- one startup command;
- `/` redirects to `/explore`;
- a clear search box and plain-language introduction;
- example searches;
- obvious loading, result, empty, error, and blocked states;
- a simple explanation of "Hunt" at the moment it becomes relevant;
- no JSON, audit IDs, internal task names, or architecture vocabulary in the normal first-use path;
- an automated browser smoke test from clean startup.
