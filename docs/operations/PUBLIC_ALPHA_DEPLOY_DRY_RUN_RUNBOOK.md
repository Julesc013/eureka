# Public Alpha Deploy Dry-Run Runbook

`PUBLIC-ALPHA-DEPLOY-DRY-RUN-00` rehearses deployment mechanics for the
read-only public alpha without deploying, publishing, changing DNS, writing
`site/dist`, or claiming production/public launch readiness.

## Inputs

- `PUBLIC-ALPHA-LAUNCH-CANDIDATE-00` result
- public alpha hosting plan
- security headers plan
- rate-limit policy
- rollback plan
- environment checklist

## Dry-Run Checks

1. Confirm the launch-candidate result is `pass`.
2. Confirm deploy manifest inputs and outputs are recorded.
3. Confirm no credentials, tokens, or provider secrets are required or
   committed.
4. Confirm smoke checks cover status, search, object, web index, no public
   write actions, and no live source fanout.
5. Confirm rollback steps identify candidate commit, prior artifact/snapshot,
   smoke-after-rollback checks, and the absence of public write state.
6. Confirm manual approval remains required before any deploy or launch task.

## Forbidden

- deployment
- public launch
- DNS changes
- hosting-provider mutation
- `site/dist` writes
- public/master index mutation
- live source calls
- public mutation
- downloads, uploads, extraction, or model/provider calls
