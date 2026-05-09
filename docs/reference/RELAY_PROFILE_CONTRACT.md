# Relay Profile Contract

`contracts/relay/relay_profile.v0.json` defines a fixture-only relay profile.

The current D-BUNDLE-02 profile is localhost-only, read-only, and explicit-input
only. Public binds, hosted relay behavior, writes, uploads, downloads, action
execution, accounts, telemetry, and live source access are all disabled.

Required boundary fields keep `bind_public_interfaces_allowed`, `write_allowed`,
`upload_allowed`, `download_allowed`, `action_execution_allowed`,
`live_source_access_allowed`, `account_auth_allowed`, and `telemetry_allowed`
false.

