# Local Search And Index Interaction

Future import has no search impact by default and no index impact by default.

Mode impact:

- `validate_only`: no search impact and no index impact
- `stage_local_quarantine`: no search impact by default and no index impact by
  default
- `inspect_staged`: no search impact and no index impact
- `local_index_candidate`: future opt-in local-only index-build input, not
  implemented in P39
- hosted public search: no impact without master-index review and hosted search
  implementation
- public static site: no impact

Source, evidence, and index packs must not affect the `local_index_only` public
runtime until an explicit import/index milestone creates an opt-in local mode
with separate validation and tests.
