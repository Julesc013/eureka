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
