# Blocked Request Verification

| forbidden parameter | expected rejection | actual status | leaked secret/path | notes |
| --- | --- | --- | --- | --- |
| q_too_long | query_too_long | None | False | Hosted backend URL not configured. |
| limit_too_large | limit_too_large | None | False | Hosted backend URL not configured. |
| mode_live_probe | live_probes_disabled | None | False | Hosted backend URL not configured. |
| mode_live_federated | live_probes_disabled | None | False | Hosted backend URL not configured. |
| include_raw_source_payload | unsupported_include | None | False | Hosted backend URL not configured. |
| index_path | local_paths_forbidden | None | False | Hosted backend URL not configured. |
| store_root | local_paths_forbidden | None | False | Hosted backend URL not configured. |
| local_path | local_paths_forbidden | None | False | Hosted backend URL not configured. |
| path | local_paths_forbidden | None | False | Hosted backend URL not configured. |
| file_path | local_paths_forbidden | None | False | Hosted backend URL not configured. |
| directory | local_paths_forbidden | None | False | Hosted backend URL not configured. |
| root | local_paths_forbidden | None | False | Hosted backend URL not configured. |
| url | forbidden_parameter | None | False | Hosted backend URL not configured. |
| fetch_url | forbidden_parameter | None | False | Hosted backend URL not configured. |
| crawl_url | forbidden_parameter | None | False | Hosted backend URL not configured. |
| source_url | forbidden_parameter | None | False | Hosted backend URL not configured. |
| download | downloads_disabled | None | False | Hosted backend URL not configured. |
| install | installs_disabled | None | False | Hosted backend URL not configured. |
| execute | installs_disabled | None | False | Hosted backend URL not configured. |
| upload | uploads_disabled | None | False | Hosted backend URL not configured. |
| source_credentials | forbidden_parameter | None | False | Hosted backend URL not configured. |
| auth_token | forbidden_parameter | None | False | Hosted backend URL not configured. |
| api_key | forbidden_parameter | None | False | Hosted backend URL not configured. |
| live_probe | live_probes_disabled | None | False | Hosted backend URL not configured. |
| live_source | live_probes_disabled | None | False | Hosted backend URL not configured. |
| network | forbidden_parameter | None | False | Hosted backend URL not configured. |
| arbitrary_source | forbidden_parameter | None | False | Hosted backend URL not configured. |

Covers local path params, arbitrary URL params, live probe params, download/install/execute/upload params, credential/token params, and mode escalation params. No backend URL was configured, so these remain required future checks rather than passed deployment evidence.
