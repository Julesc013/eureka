# AIDE Release Notes Preview

This is a deterministic preview only. It does not publish a release.

## Added

- runtime/local_worker, worker runner scripts, LOCAL-09 policies, inventories, docs, tests, validator, queue handoff, and audit pack.
- target-local Git workflow detection and helper planning reports.
- Q32 final evidence and review-gate status.
- deterministic local auto-test and auto-search harness commands.
- machine-readable and Markdown eval reports with latency and safety posture.
- read-only LAN safety policy package, LAN route/mutation matrices, policy check script, validator, docs, and audit pack.
- LOCAL-12 LAN smoke/probe/shutdown scripts, validator, policies, inventories, tests, docs, and audit pack.
- LOCAL-13 clean-machine scripts, validator, policies, inventories, tests, docs, and audit pack.
- LOCAL-14 closeout scripts, inventories, docs, tests, audit pack, and task stubs.
- final green inventories and audit evidence.
- LOCAL total remediation inventories, audit evidence, and promotion gate tests.
- final state inventories, audit pack, future execution plan, and chat alignment packet.

## Changed

- WorkUnit queue now records worker result and audit payload references.
- imported canonical AIDE governance and validation tooling into Eureka.
- regenerated Eureka-local AIDE packets and governance reports.
- refreshed agent guidance for structured commits, task recovery, and Git plan usage.
- refreshed final Q32 reports and token metadata.
- local server now requires explicit --bind-lan for all-interface bind hosts and blocks LAN unsafe routes.
- AIDE queue/context/repo-health to hand off to LOCAL-13.
- AIDE queue/context/repo-health to hand off to LOCAL-14.
- AIDE queue/context/repo-health to hand off from LOCAL-14 to HUNT-00.
- completed LOCAL validators accept advanced queue state.
- final green evidence records one additional safe repair.
- LOCAL closeout warning and promotion evidence now reflect zero new unallowlisted leakage findings.
- promotion evidence now records the completed fast-forward promotion.
- LOCAL-14 promotion review evidence restored to plan-only semantics.

## Fixed

- LAN client host handling is separated from service bind-host validation.
- stale IA readiness and local workbench test expectations.
- refreshed stale public search generated artifacts.
- runtime leakage path classification now treats nested product tests as test fixtures before production paths.
- runtime leakage term matching keeps uppercase governance tokens case-sensitive.
- runtime leakage glob matching handles mid-pattern ** fixture paths.

## Notes

- 12 malformed commits were excluded from release-note grouping.
