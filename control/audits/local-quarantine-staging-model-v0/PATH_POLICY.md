# Path Policy

Future staging roots must be user controlled. Allowed future root classes are
user-configured cache roots, application-local data roots, and repo-local
ignored development roots.

Suggested development root: `.eureka-local/`.

Ignored companion roots:

- `.eureka-cache/`
- `.eureka-staging/`

Forbidden roots:

- `site/dist`
- `site/`
- public data
- `external`
- `runtime`
- canonical `control/inventory` source files
- `evals`
- `snapshots/examples`
- `crates`
- `docs`

This pack adds ignore policy only. It does not create local staging
directories.
