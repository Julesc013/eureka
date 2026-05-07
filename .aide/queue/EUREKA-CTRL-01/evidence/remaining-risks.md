# EUREKA-CTRL-01 Remaining Risks

- Comment-density bands are advisory only and do not hard-fail existing source
  code.
- The changelog preview tool is local preview support, not release automation
  and does not mutate `CHANGELOG.md` by default.
- The existing AIDE commit hook policy was aligned with the new required
  `aide` type and `## Why` heading so this task can use the requested commit
  subject and body.
- AIDE Lite `verify` and `review-pack` remain WARN-only because compact task
  scope metadata does not exactly enumerate the new control paths and the latest
  review packet references optional AIDE status artifacts that are not present.
