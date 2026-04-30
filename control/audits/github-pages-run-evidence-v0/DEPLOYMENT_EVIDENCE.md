# Deployment Evidence

Deployment records were inspected through the GitHub repository deployments API.

Current-head deployment record:

- Deployment ID: `4537439755`
- SHA: `8372ca71a3877de18503acfa34fb15d5685b38c6`
- Ref: `main`
- Environment: `github-pages`
- Task: `deploy`
- Created: `2026-04-30T14:46:02Z`
- Updated: `2026-04-30T14:46:18Z`

Deployment statuses:

- `in_progress` at `2026-04-30T14:46:07Z`
- `failure` at `2026-04-30T14:46:18Z`

Environment URL:

- Empty in deployment status.

Pages site API:

- `GET /repos/Julesc013/eureka/pages` returned `404 Not Found`.

URL check:

- No URL was available to check.
- No site URL was fetched.

Deployment success claim allowed: no.

Reason:

The deployment status is `failure`, no Pages artifact was uploaded, the deploy step was
skipped, and no environment URL was emitted.
