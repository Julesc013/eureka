# Static To Dynamic Handoff

The static site is the public front door. Dynamic search remains a separate
future hosted backend.

Handoff rules:

- default to backend unconfigured;
- enable a hosted search form only after a verified backend URL and evidence
  reference exist;
- keep the form GET-based and no-JS-compatible;
- cap query input at 160 characters;
- keep `local_index_only` visible;
- do not hardcode localhost or a fake hosted URL into generated public pages;
- keep GitHub Pages static-only and do not imply Python runs there.

P56 records the handoff contract in static public data and generated pages, but
it does not perform hosting work.
