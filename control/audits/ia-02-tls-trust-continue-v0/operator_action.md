# Operator Action

Action class: `valid_ca_bundle_env_needed_for_current_shell`

The safe local action used for this task was to set `SSL_CERT_FILE` for the
current shell only to an existing local CA bundle provided by the active Python
installation. This did not disable TLS verification and did not commit a CA
certificate or machine-specific path.

No machine-admin certificate-store mutation was performed by repo scripts.

