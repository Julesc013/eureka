# Action And Risk Guidance

Public Search Result Card Contract v0 separates actions into:

- `allowed`: read-only or inspection-oriented actions.
- `blocked`: actions prohibited in v0.
- `future_gated`: actions that require a later policy and implementation.

Allowed concepts are limited to:

- `inspect`
- `preview`
- `read`
- `cite`
- `export_manifest`
- `view_provenance`
- `compare`
- `view_source`
- `view_absence_report`

Blocked or future-gated concepts include:

- `download`
- `download_member`
- `mirror`
- `install_handoff`
- `package_manager_handoff`
- `emulator_handoff`
- `vm_handoff`
- `execute`
- `restore_apply`
- `uninstall`
- `rollback`
- `upload`
- `submit_private_source`

The presence of a future-gated action is not permission to perform it. It means
the card is honest about a user desire while preserving the v0 safety boundary.

## Rights

The rights block records uncertainty and source-term caveats. It must not claim
rights clearance. `distribution_allowed: "unknown"` means the card is not
granting distribution permission.

## Risk

The risk block records executable risk and malware-scan status. It must not
claim malware safety. v0 cards should use `not_scanned`, `unavailable`,
`future`, or `not_applicable` rather than implying a scan exists.

## Safety Boundaries

Cards must not include download URLs, install URLs, executable handoff URLs,
private local paths, raw source payloads, source credentials, or claims that an
artifact is safe to execute.
