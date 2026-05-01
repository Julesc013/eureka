# Request Contract

Canonical schema: `contracts/api/search_request.v0.json`.

Required:

- `q`: string, trimmed by runtime, minimum length after trim 1, maximum 160.

Optional:

- `limit`: default 10, maximum 25.
- `offset`: experimental local/prototype offset.
- `cursor`: future pagination token.
- `profile`: `standard_web`, `lite_html`, `text`, `api_client`, `snapshot`,
  or `native_client`.
- `mode`: active value `local_index_only` only.
- `include`: safe summary expansions such as `evidence`, `compatibility`,
  `source_summary`, `limitations`, `gaps`, and `actions`; old summary aliases
  remain accepted for compatibility.

Forbidden parameters include local paths and roots, arbitrary URLs, network
source controls, downloads, installs, execution, uploads, user files,
credentials, API keys, live probes, live sources, and arbitrary source controls.
