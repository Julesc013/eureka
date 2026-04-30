# Telemetry And Logging Policy

Telemetry and Logging Policy v0 defines Eureka's default posture for future
native clients, diagnostics, logs, and public-alpha reporting. It is policy work
only. No telemetry, analytics, diagnostics upload, crash-report upload,
accounts, cloud sync, or native-client runtime is implemented.

## Defaults

- Telemetry is not implemented.
- Telemetry must be off by default if it is ever added.
- Analytics are not implemented.
- External uploads are disabled by default.
- Crash-report uploads are disabled by default.
- Diagnostics exports are future explicit user actions only.
- Manual external observations are user-entered records, not telemetry.

## Logs

Logs are local developer/runtime artifacts, not analytics. Logs should avoid
private paths, credentials, tokens, source secrets, account/session values, and
private inventories where possible.

Public-alpha status and logs must not expose secrets or private local paths.
Static public data, snapshots, checkpoint reports, and public pages must not
embed private absolute paths.

## Diagnostics And Crash Reports

Future diagnostics or crash reports must be explicit opt-in exports. They must
show what will be included, redact private paths and secrets where possible,
and avoid uploading anything automatically.

No clean/safe executable verdict, malware scan result, rights clearance, or
production readiness statement may be inferred from logs or diagnostics.

AI Provider Contract v0 keeps prompt logging, output logging, telemetry, and
external log upload disabled by default. No AI prompt log runtime, model-call
log runtime, provider telemetry, analytics, or remote diagnostics upload is
implemented.

## Credentials And Accounts

No account system exists. No credential store exists. Source credentials,
tokens, cookies, private keys, account/session data, and cloud identity state
must not be written to public data, snapshots, relay old-client projections, or
support exports.

Future account, credential, or sync work requires a separate policy and
validation lane.

## Not Implemented

This policy does not implement telemetry, analytics, log upload, diagnostics
upload, crash-report upload, accounts, source credentials, cloud memory, cloud
sync, native clients, relay runtime, or production monitoring.
