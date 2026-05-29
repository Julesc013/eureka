# Post Public Alpha Deploy Dry-Run Plan

After the dry run passes, the next safety step is:

`DEV-TO-MAIN-PROMOTION-REVIEW-05`

That promotion should move both launch-candidate and deploy dry-run evidence to
`main`. Only after that promotion should `PUBLIC-ALPHA-LAUNCH-00` be considered,
and launch still requires explicit manual approval.

This plan does not authorize deployment, public launch, production readiness
claims, live source fanout, public mutation, downloads, extraction, or
model/provider calls.
