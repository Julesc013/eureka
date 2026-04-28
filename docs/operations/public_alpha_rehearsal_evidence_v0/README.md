# Public Alpha Rehearsal Evidence v0

This pack records supervised local rehearsal evidence for Eureka's current static site and public-alpha safe-mode posture.

It is evidence and runbook material only. It does not deploy Eureka, approve production, add live probes, or record external baseline observations.

No public deployment happened.

LIVE_ALPHA_01 adds a public alpha wrapper after this evidence snapshot; it still performs no deployment, keeps live probes disabled, and does not approve production.

Public Publication Plane Contracts v0 now sits after the wrapper and before GitHub Pages deployment enablement. It governs routes, client profiles, public data, base-path portability, deployment targets, redirects, and public claim traceability without deploying, adding a generator, or enabling live backend behavior.

## Contents

- `REHEARSAL_SCOPE.md`
- `COMMIT_AND_ARTIFACTS.md`
- `STATIC_SITE_EVIDENCE.md`
- `SAFE_MODE_EVIDENCE.md`
- `ROUTE_INVENTORY_EVIDENCE.md`
- `EVAL_AND_AUDIT_EVIDENCE.md`
- `EXTERNAL_BASELINE_STATUS.md`
- `OPERATOR_CHECKLIST_STATUS.md`
- `BLOCKERS_AND_LIMITATIONS.md`
- `NEXT_DEPLOYMENT_REQUIREMENTS.md`
- `SIGNOFF_TEMPLATE.md`
- `rehearsal_evidence_manifest.json`

## Current Summary

- branch: `main`
- recorded commit sha: `101d9131bad4e745fe722ba633d5d579750b81b2`
- static site validation: `valid`
- public-alpha smoke: `passed`
- signoff status: `unsigned`

Run `python scripts/generate_public_alpha_rehearsal_evidence.py --check` to validate the pack.

