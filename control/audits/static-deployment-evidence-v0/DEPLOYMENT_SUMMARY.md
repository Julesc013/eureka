# Deployment Summary

P52 found the local static publication path intact:

- `.github/workflows/pages.yml` runs on `main` pushes and
  `workflow_dispatch`.
- The workflow builds and validates `site/dist`.
- The workflow uploads `site/dist`, not the retired static artifact root.
- Local artifact checks pass after serial recheck.
- GitHub CLI is unavailable in this environment, so current-head GitHub
  Actions and Pages API evidence could not be collected locally.

Committed prior evidence under
`control/audits/github-pages-run-evidence-v0/` records a failed Pages workflow
run for commit `8372ca71a3877de18503acfa34fb15d5685b38c6`: the job failed at
`actions/configure-pages@v5`, no artifact was uploaded, no deployment URL was
emitted, and the Pages API returned `404 Not Found`.

P52 does not prove that the site is deployed. The deployment status is
`deployment_unverified`, with prior committed evidence of `deployment_failed`
and current operator action required.
