# Promotion Decision

Decision: `conditionally_promoted_pending_github_actions_evidence`

`site/dist/` is promoted as Eureka's active repo-local static publication
artifact and the only current artifact configured for GitHub Pages upload.

The decision is conditional because this review did not inspect or record a
successful GitHub Actions deployment run. Local artifact validity and workflow
readiness are established; public deployment success remains unverified.

## Established

- `site/dist/` exists and validates locally.
- `public_site/` is absent as an active artifact.
- `.github/workflows/pages.yml` uploads `site/dist`.
- Generated artifact inventory owns `static_site_dist`.
- Drift guard checks `static_site_dist`.
- Static safety checks pass locally.
- Public data, lite/text/files surfaces, resolver demos, and snapshot references
  validate locally.

## Not Claimed

- no GitHub Pages deployment success claim
- no production-readiness claim
- no backend hosting
- no public search runtime or API route
- no live probe, crawler, external search automation, or URL fetching
- no custom domain setup
