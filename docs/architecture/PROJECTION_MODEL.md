# Projection Model

Projection profiles define who can see which packet fields and who can invoke which actions. Permission differences are projection policy, not separate product semantics.

The required profiles are operator_workbench, local_user_read_only, public_web, public_api, cli, tui, relay_client, snapshot_client, native_desktop_read_only, mobile_read_only, and future_marketplace_admin.

Operator Workbench can see internal lanes and may perform policy-gated review, preview, rebuild, and export actions. Public web and public API are read-only restricted projections. Relay, snapshot, native desktop, and mobile profiles are read-only initially. CLI and TUI inherit an explicit operator or local profile; they are not bypass channels.

Public and native default modes forbid source probes, downloads, uploads, extraction, model/provider calls, reviewed-index mutation, master-index mutation, deployment, raw source-cache access, private local paths, operator tokens, and unreviewed truth claims.
