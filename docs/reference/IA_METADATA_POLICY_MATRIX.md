# IA Metadata Policy Matrix

| Area | IA-00 decision |
| --- | --- |
| Connector status | Policy approved, runtime disabled |
| Live metadata calls | Disabled |
| Fixture replay | Required before live probe |
| Operator approval | Required before IA-02 |
| User-Agent/contact | Required before live |
| Rate limits | Required before live |
| Timeout/retry/backoff | Required before live |
| Retry-After | Required before live |
| Cache | Required before repeat/live pilot |
| Kill switch | Required and fail-closed |
| Downloads | Forbidden |
| Uploads/write APIs | Forbidden |
| Public search fanout | Forbidden |
| Source-cache writes | Forbidden in IA-00 |
| Evidence writes | Forbidden in IA-00 |
| Candidate/reviewed/master index mutation | Forbidden in IA-00 |
| Accepted truth from metadata alone | Forbidden |
| Production/public readiness claim | Forbidden |
| Fixture replay | IA-01 local committed fixtures only |

See `control/inventory/ia_metadata_allowed_endpoint_matrix.json` and
`control/inventory/ia_metadata_forbidden_action_matrix.json` for machine-readable
policy rows.
