# H1 Metadata Fixture Replay

Fixture replay loads committed fixtures from `examples/connectors/h1_metadata_wave/fixtures/`, normalizes them, and builds replay results. By default it writes no files. Explicit outputs are allowed only under audit generated roots, replay examples, or temporary test directories.

Replay proves parsing only. It does not write source cache, evidence ledger, review queue, public index, or master index state.
