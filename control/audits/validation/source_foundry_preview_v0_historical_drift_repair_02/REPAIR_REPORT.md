# Historical Validator Drift Repair Report

Status: `READY_FOR_EXTERNAL_FULL_DISCOVERY_RERUN`

## Summary

This repair resolved the remaining Source Foundry Preview v0 historical
validator drift with targeted checks only.

Repairs applied:

- added explicit Source Foundry successor semantics to HUNT, LOCAL,
  public-alpha defer, IA readiness, and dev-to-main historical validators;
- classified `LICENSE.md`, `LICENSE-SUMMARY.md`, and `NOTICE.md` as
  conventional top-level root files in the repo-canon contract;
- refined repository-layout scanning so normal third-party material/license
  language is not mistaken for the retired outside-reference root;
- replaced the obsolete "no staging tool exists" assertion with safety checks
  for local/private, non-mutating staging posture.

## Classification Totals

- historical queue expectation drift repaired: 27
- historical validator drift repaired: 20
- obsolete test candidate repaired: 1
- environment/harness slow aggregate: 2
- genuine product regressions remaining: 0
- unknown failures remaining: 0

## Safety

- full discovery inside AI session: false
- main promotion: false
- reviewed records created: false
- reviewed/master mutation: false
- public-index mutation: false
- evidence/candidate/review store mutation: false
- provider/network calls: false
- downloads/file fetches: false
- public exposure: paused
- license posture: unchanged

## External Rerun Posture

A single fresh external full-discovery rerun is now justified after these
tracked repairs are committed and pushed.

Do not reuse `source_foundry_preview_v0_checkpoint_00`.

Use the new run ID:

```text
source_foundry_preview_v0_post_historical_repair_02
```
