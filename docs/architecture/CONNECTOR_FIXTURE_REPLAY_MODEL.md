# Connector Fixture Replay Model

Fixture replay is the first executable step in the connector lifecycle.

The workflow is:

1. Pick a source record and connector family.
2. Load a committed fixture.
3. Run a pure normalizer or identity replay.
4. Wrap the result in a connector output envelope.
5. Validate truth and product boundaries.
6. Produce audit evidence.

Replay is not a live probe. It is not source sync. It does not write source
cache, evidence ledger, review queue, public index, or master index state.
