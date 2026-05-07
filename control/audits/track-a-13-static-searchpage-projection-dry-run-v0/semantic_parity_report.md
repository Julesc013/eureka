# TRACK-A-13 Semantic Parity Report

Generated dry-run projections were compared against SearchPageView semantic categories.

| Semantic Category | standard_static_html | lite_static_html | text_static | file_tree_static | static_json_handoff |
| --- | --- | --- | --- | --- | --- |
| route_identity | preserved | preserved | preserved | preserved | preserved |
| query_identity | preserved | preserved | preserved | preserved | preserved |
| public_runtime_posture | preserved | preserved | preserved | preserved | preserved |
| result_identity | preserved | preserved | preserved | degraded_but_preserved | preserved |
| source_evidence_posture | preserved | preserved | preserved | degraded_but_preserved | preserved |
| risk_rights_posture | preserved | preserved | preserved | preserved | preserved |
| compatibility_posture | preserved | preserved | preserved | preserved | preserved |
| limitations | preserved | preserved | preserved | preserved | preserved |
| blocked_actions | preserved | preserved | preserved | preserved | preserved |
| next_safe_actions | preserved | preserved | preserved | preserved | preserved |
| hosted_live_download_upload_account_telemetry_non_claims | preserved | preserved | preserved | preserved | preserved |

## Notes

- File-tree output intentionally degrades result/source detail into a README summary while preserving status and caveats.
- No generated output is an active public route, live API, deployment artifact, hosted backend, or production claim.
- Site artifacts under `site/dist` were not regenerated or changed.
