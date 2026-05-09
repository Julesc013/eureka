# Extraction Sandbox Model

F-BUNDLE-01 introduces a fixture-only extraction sandbox below the H1 metadata-wave handoff. It inspects synthetic repo-local containers under `examples/extraction/fixtures/` and emits preview artifacts under examples, audit generated output, or temp-test directories.

The model is deliberately narrow:

- Tier 0 collects outer metadata and checksum.
- Tier 1 lists members and blocks unsafe paths, symlinks, special files, and bomb-risk containers.
- Tier 2 reads small allowlisted manifest-like members into bounded previews.

The sandbox does not execute, install, download, crawl, call networks, recurse into nested archives, or mutate runtime state.
