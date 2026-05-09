# Extraction Fixture Policy

Allowed inputs are committed fixtures under `examples/extraction/fixtures/`, target records under `examples/extraction/targets/`, and explicit temp-test fixtures. The runner rejects private-looking paths and arbitrary repo paths.

Fixture builders create tiny deterministic ZIP/TAR archives in their own directories only. They do not download, call APIs, execute payloads, or inspect private files.
