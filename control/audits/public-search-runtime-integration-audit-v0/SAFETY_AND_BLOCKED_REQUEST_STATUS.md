# Safety And Blocked Request Status

Public search safety is active for local/prototype routes.

Validated forbidden behavior includes:

- `live_probe` and `live_source` parameters: blocked.
- Arbitrary URL parameters such as `url`, `fetch_url`, `source_url`: blocked.
- Local path/root parameters such as `index_path`, `store_root`, `local_path`:
  blocked.
- Source-cache/evidence-ledger path parameters: not accepted public-search
  parameters; caller-provided local paths remain blocked.
- Connector parameters: not accepted for public-search live fanout.
- Download/install/execute/upload parameters: blocked.
- Token/API key/credential parameters: blocked.
- Too-long query: blocked.
- Too-large limit: blocked.

Relevant validation commands:

- `python scripts/validate_public_search_safety.py`
- `python scripts/validate_local_public_search_runtime.py`
- `python scripts/public_search_smoke.py`
- `python scripts/public_search_smoke.py --json`
- `python scripts/run_public_search_safety_evidence.py`
- `python scripts/validate_public_search_safety_evidence.py`

