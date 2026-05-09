# IA Metadata Live Probe

The IA metadata live probe is the first controlled live-source boundary for
the Internet Archive connector lane. It is designed to perform at most one
metadata endpoint read for one explicitly approved identifier.

Current status: `blocked`.

The committed policy state does not approve live access, so the CLI and runtime
return a blocked preflight report before any network call.

## Scope

Allowed after approval:

- one `GET` to `https://archive.org/metadata/{identifier}`
- one exact identifier from the committed allowlist
- metadata JSON normalization into preview-only shapes

Still forbidden:

- broad search
- advancedsearch
- downloads
- item file fetches
- scraping or crawling
- public-query fanout
- source sync
- public-index or master-index mutation
- evidence, candidate, or public truth acceptance

## Outputs

The runtime can build:

- live probe result
- normalized metadata record
- source cache candidate preview
- evidence candidate preview
- review queue seed preview
- live probe summary

All outputs are source observations or review seeds only.

## Commands

Dry preflight:

```text
python scripts/run_ia_metadata_live_probe.py --identifier eureka-software-fixture --check
```

Offline validation:

```text
python scripts/validate_ia_metadata_live_probe.py
```
