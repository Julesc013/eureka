# Deployment Evidence

Current P52 local evidence:

- `gh --version`: unavailable; `gh` command not found.
- `gh auth status`: unavailable; `gh` command not found.
- `gh workflow list`: skipped because `gh` is unavailable.
- `gh run list --workflow pages.yml --limit 10`: skipped because `gh` is
  unavailable.
- `gh api repos/Julesc013/eureka/pages`: skipped because `gh` is unavailable.

Committed historical evidence:

- Prior Pages run evidence exists under
  `control/audits/github-pages-run-evidence-v0/`.
- That evidence records a failed run, no uploaded artifact, no deployment URL,
  and Pages API `404 Not Found`.
- The prior failed run was for an older commit, so it is evidence of the
  operator/settings blocker, not proof of current-head Actions status.

Deployment URL:

```text
unverified
```

Deployment success claim allowed:

```text
false
```
