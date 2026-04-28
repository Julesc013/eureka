# Base Path Portability

Eureka's static publication plane must remain portable between the current
GitHub Pages project path and future root-hosted static targets.

Current project base path:

```text
/eureka/
```

Future custom-domain or alternate-host base path:

```text
/
```

## Link Rule

Static artifact links should be relative:

```text
status.html
data/site_manifest.json
../data/source_summary.json
```

Static artifact links should not be root-relative:

```text
/status.html
/data/source_summary.json
```

Root-relative route names are allowed in contracts and JSON route registries
because those are route identifiers, not clickable static links.

## Canonical URL Policy

The current governed project URL is:

```text
https://julesc013.github.io/eureka/
```

Static pages should not add absolute canonical links to that URL or to a future
custom domain until a future domain task updates the publication inventory.

## Data References

Public data summaries under `public_site/data/` are static files. Pages,
lite/text/files surfaces, demo snapshots, and future generated output should
reference them with relative paths so the same artifact can be served under
`/eureka/` or `/`.

## Local Preview

Opening files with `file://` can be useful for quick inspection, but browser
behavior for relative links, MIME types, and local security rules varies. Local
preview is not a public host and is not evidence that a domain is configured.

## Generator Responsibility

`site/build.py` and other static generators must preserve relative links and
avoid embedding root-only assumptions. If a future host needs absolute
canonical URLs, that must be a separately governed contract change.
