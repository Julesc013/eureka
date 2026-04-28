# Public Route Contract

Public routes are registered in
`control/inventory/publication/page_registry.json`.

Every current public route record must include:

- `path`
- `title`
- `status`
- `stability`
- `source_file`
- `client_profiles`
- `requires_javascript`
- `requires_css`
- `works_under_project_base_path`
- `safe_for_static_hosting`
- `public_claim_scope`
- `notes`

Current implemented and `static_demo` routes point at files under
`public_site/`. Reserved future routes use `source_file: null` and must stay
`planned`, `deferred`, `blocked`, or another non-implemented status until an
artifact exists.

Routes must work under the GitHub Pages project base path `/eureka/` and under a
future custom-domain root `/`. Relative links are preferred for static pages.

Lite/Text/Files Seed Surfaces v0 promotes `/lite/`, `/text/`, and `/files/` to
`static_demo` route families backed by committed files. `/app/`, `/web/`,
`/data/` as a route root, `/api/`, and `/snapshots/` remain reserved route
families. Their presence in the registry is reservation only, not an
implementation claim.

Static Resolver Demo Snapshots v0 promotes `/demo/` and the committed
`/demo/*.html` snapshot pages to `static_demo` routes. These routes are
fixture-backed static examples only; they are not live search routes, API
routes, backend hosting, or production resolver claims.

Custom Domain / Alternate Host Readiness v0 does not promote any new public
route. It reinforces that all existing static routes must keep relative links
and remain portable between the GitHub Pages project base path `/eureka/` and a
future root-hosted static target `/`.

Live Backend Handoff Contract v0 reserves `/api/v1/` plus specific future
endpoint templates in `live_backend_routes.json`. These are not static pages,
not GitHub Pages routes, and not live backend routes today. Static pages may
describe `/api/v1` as future/reserved but must not link to it as an available
service.
