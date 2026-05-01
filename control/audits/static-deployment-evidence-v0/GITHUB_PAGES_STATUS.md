# GitHub Pages Status

Classification values for P52:

```text
workflow_configured
deployment_unverified
deployment_failed
pages_not_enabled
gh_unavailable
operator_gated
```

Current-head live evidence could not be collected with GitHub CLI because `gh`
is not installed in this environment.

Committed prior evidence:

- Audit pack:
  `control/audits/github-pages-run-evidence-v0/`
- Run ID: `25171991131`
- Run URL:
  `https://github.com/Julesc013/eureka/actions/runs/25171991131`
- Head SHA at collection:
  `8372ca71a3877de18503acfa34fb15d5685b38c6`
- Conclusion: `failure`
- Failed step: `Configure GitHub Pages`
- Pages API status at that evidence collection: `404_not_found`
- Artifact upload: skipped
- Deployment URL: unavailable

Because that evidence is not for the current P52 head and no live `gh` query
was possible here, P52 keeps current deployment success unverified.
