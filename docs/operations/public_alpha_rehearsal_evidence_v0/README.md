# Public Alpha Rehearsal Evidence v0

This pack records supervised local rehearsal evidence for Eureka's current static site and public-alpha safe-mode posture.

It is evidence and runbook material only. It does not deploy Eureka, approve production, add live probes, or record external baseline observations.

No public deployment happened.

LIVE_ALPHA_01 adds a public alpha wrapper after this evidence snapshot; it still performs no deployment, keeps live probes disabled, and does not approve production.

Public Publication Plane Contracts v0 sits after the wrapper and governs static generation plus any later live backend handoff. It governs routes, client profiles, public data, base-path portability, deployment targets, redirects, and public claim traceability without enabling live backend behavior.

GitHub Pages Deployment Enablement v0 now configures a static-only workflow for public_site. It does not host the Python backend, enable live probes, add a custom domain, or prove deployment success without GitHub Actions evidence.

Static Site Generation Migration v0 now adds a stdlib-only site generator and site/dist validation output, but public_site remains the deployable GitHub Pages artifact. The generated output is not a backend, live probe, custom domain, or production-readiness claim.

Generated Public Data Summaries v0 now adds deterministic static JSON under public_site/data and site/dist/data. Those files are static summaries only; they are not a live API, live probe, external observation record, or production JSON stability claim.

Lite/Text/Files Seed Surfaces v0 now adds static compatibility outputs under public_site/lite, public_site/text, and public_site/files, with generated copies under site/dist. These surfaces are no-JS/no-download publication artifacts only; they are not live search, executable mirrors, signed snapshots, relay runtime, native-client runtime, or public-alpha backend approval.

Static Resolver Demo Snapshots v0 now adds static fixture-backed examples under public_site/demo, with generated copies under site/dist/demo. These examples are no-JS publication artifacts only; they are not live search, a live API, backend hosting, external observations, or production behavior.

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
- recorded commit sha: `afb55dd28514036e843967bf90db7da9084b8188`
- static site validation: `valid`
- public-alpha smoke: `passed`
- signoff status: `unsigned`

Run `python scripts/generate_public_alpha_rehearsal_evidence.py --check` to validate the pack.

