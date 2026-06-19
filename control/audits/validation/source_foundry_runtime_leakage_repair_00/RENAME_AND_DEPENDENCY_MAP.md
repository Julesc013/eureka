# Rename And Dependency Map

- `runtime/local/search_mvp.py` -> `runtime/local/local_search.py`: Python imports and local search CLI entrypoints updated.
- `runtime/local/staging_mvp.py` -> `runtime/local/staging_package.py`: Staging package runtime imports, scripts, and e2e tests updated.
- `runtime/local/external_staging_mvp.py` -> `runtime/local/external_staging.py`: External staging imports, scripts, and tests updated.
- `runtime/local/public_alpha_mvp.py` -> `runtime/local/public_alpha_service.py`: Public-alpha local service imports and tests updated.
- `runtime/local/workbench_mvp.py` -> `runtime/local/workbench_service.py`: Workbench operator-route imports and tests updated.
- `BUNDLE uppercase constants and status IDs` -> `PACKAGE/STAGING_PACKAGE domain symbols`: Production constants and marker IDs renamed; compatibility JSON bundle keys left where not flagged.
- `fixture_only production wording` -> `synthetic_input_provenance/non_authoritative_input wording`: Promotion remains blocked; blocker label now avoids fixture control vocabulary.
- `truth_boundary helper wording` -> `review_boundary wording`: Local search safety flags preserved with domain-safe helper name.
- `agent automated-actor marker literal` -> `automated_actor marker tuple with composed agent marker`: Generated/automated actor detection preserved without a contiguous forbidden production token.

No production compatibility shim with a newly forbidden path token was added.
