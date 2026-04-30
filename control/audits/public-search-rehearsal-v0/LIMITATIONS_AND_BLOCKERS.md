# Limitations And Blockers

## Passed Local Rehearsal

- Local runtime route checks passed.
- Safe query checks passed, including valid zero-result cases.
- Blocked request checks passed with governed error codes.
- Static handoff review passed.
- Public-alpha route posture remains constrained.

## Remaining Limitations

- Hosted public search is unavailable.
- GitHub Pages remains static-only and cannot run the Python runtime.
- Search usefulness is still fixture/local-index limited.
- No hosted rate-limit middleware or production abuse controls exist.
- No operator-approved hosted backend URL exists.
- Live probes remain disabled and require separate explicit approval.
- Downloads, installs, uploads, accounts, telemetry, and local path search remain
  disabled.

## Blockers For Hosted Rehearsal

- Hosted backend plan and operator signoff are still needed.
- Rate-limit and timeout controls must be reviewed before public exposure.
- GitHub Pages deployment evidence remains separate from public search runtime
  evidence.
- Live probe approval must not be inferred from this rehearsal.
