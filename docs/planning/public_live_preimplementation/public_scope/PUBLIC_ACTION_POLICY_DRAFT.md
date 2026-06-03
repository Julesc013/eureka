# Public Action Policy Draft

| Affordance | Public Alpha Class |
| --- | --- |
| `view` | public_alpha_allowed |
| `inspect_evidence` | public_alpha_allowed |
| `compare` | public_alpha_allowed when read-only |
| `cite` | public_alpha_allowed |
| `export_manifest` | public_alpha_allowed if public-safe |
| `watch_need` | future_gated |
| `report_issue` | public_alpha_allowed only through external/non-mutating channel |
| `review_candidate` | operator_only |
| `promote` | operator_only |
| `reject` | operator_only |
| `rebuild_index` | operator_only |

Unsafe for v1: download, install, launch emulator, run extraction, submit direct
evidence into product truth, crawl source, arbitrary live lookup, mutate
records.

