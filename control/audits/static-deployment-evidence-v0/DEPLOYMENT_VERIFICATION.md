# Deployment Verification

P52 verification establishes local readiness only:

- the workflow is configured for the static artifact
- the local `site/dist` artifact validates
- the static artifact checker passes
- no backend, live search, live probes, or dynamic host is deployed by the
  workflow

P52 does not verify a live Pages deployment. Verification remains incomplete
until an operator records a successful workflow run and deployed URL.

Required future evidence for `deployment_verified=true`:

- successful Pages workflow run ID
- run URL
- deployed commit SHA
- Pages deployment URL
- deployed root/status/sources/search/lite/text/files page checks
- timestamp from workflow, Pages API, or committed evidence
