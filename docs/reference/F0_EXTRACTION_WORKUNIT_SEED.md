# F0 Extraction WorkUnit Seed

An F0 ExtractionWorkUnitSeed is a dry-run suggestion. It may propose future actions such as inspect_file_manifest, review_member_manifest, block_unsafe_container, or defer_download_required, but it does not create a runtime WorkUnit by itself.

The seed is fixture-only and manifest-only in this foundation. It is not truth, does not create evidence, and stays review-gated.

Boundary defaults:

- allowed is false by default
- no downloads
- no filesystem extraction
- no execution
- no arbitrary file extraction
- no operator instance mutation
- no master/public index mutation

A later task may turn a seed into an operator-approved WorkUnit, but only after explicit policy and review gates exist.
