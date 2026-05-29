# Post Public Alpha Deploy Dry-Run Promotion Plan

After external full discovery passes for `DEV-TO-MAIN-PROMOTION-REVIEW-05`:

1. Resume the promotion review.
2. Verify branch state still supports fast-forward promotion.
3. Verify deploy dry-run and launch-candidate validators still pass.
4. Fast-forward `main` to `dev`.
5. Verify `origin/main == origin/dev`.

Only after that promotion may `PUBLIC-ALPHA-LAUNCH-00` be considered, and that
task still requires explicit manual launch approval.
