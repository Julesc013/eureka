# GitHub Protection And CI Advisory

This AIDE reference describes the local, report-only GitHub protection and CI
advisory surface.

The advisory is intentionally non-mutating:

- it does not call the GitHub API
- it does not install or edit `.github/workflows`
- it does not create tags or releases
- it does not push branches
- it does not call providers or models
- it does not perform network calls

The generated advisory may inspect target branch names and existing workflow
files to produce local guidance, but existing target workflows are target state,
not AIDE-created mutation. Any future live GitHub operation requires a separate
reviewed task with explicit operator approval.

