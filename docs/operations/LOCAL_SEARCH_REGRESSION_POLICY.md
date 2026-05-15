# Local Search Regression Policy

LOCAL-10 treats search failures as reportable local regression evidence. The
harness uses fixed queries and records per-query status so failures are visible
in JSON and Markdown instead of being anecdotal.

The policy for this phase:

- fixed local query suite only
- local reviewed index only
- absence means local/current-index absence only
- no synthetic generation
- no live source expansion
- no source probes
- no extraction
- no model/provider calls
- no master-index mutation

Future work may expand query generation or source coverage only through a
reviewed queue item with explicit policy changes.
