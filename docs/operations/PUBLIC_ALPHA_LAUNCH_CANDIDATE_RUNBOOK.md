# Public Alpha Launch Candidate Runbook

This runbook is for the final gate before a public-alpha deploy dry run. It does
not deploy, publish, or claim launch readiness.

## Inputs

- promoted `main == dev` public alpha baseline
- `DEV-TO-MAIN-PROMOTION-REVIEW-04` pass evidence
- public alpha read-only closeout evidence
- hosting readiness evidence
- snapshot relay evidence
- prior external full discovery pass

## Checks

1. Confirm branch state is clean and `origin/main == origin/dev`.
2. Confirm public alpha web and API routes are read-only.
3. Confirm no public mutation, live source fanout, downloads, extraction, or
   model/provider calls are enabled.
4. Confirm security, rate-limit, observability, privacy, abuse, and rollback
   plans exist.
5. Confirm manual approval is required before any deploy or launch task.
6. Confirm no deployment or launch claim occurred in this task.

## Output

If all gates pass, the next task is `PUBLIC-ALPHA-DEPLOY-DRY-RUN-00`.
