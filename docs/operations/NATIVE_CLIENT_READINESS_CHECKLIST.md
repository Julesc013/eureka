# Native Client Readiness Checklist

Status: future/unsigned.

Native Client Contract v0 does not approve native app implementation. This
checklist records what a later operator/reviewer must confirm before any
Windows, macOS, or other native client project starts.

## Required Review

- [ ] Public data contract is stable enough for the proposed client scope.
- [ ] Snapshot consumer contract has been reviewed for the target client.
- [ ] Native client lane has been selected from `native_client_lanes.json`.
- [ ] Build/test host for the selected lane is available.
- [ ] Action, security, rights, download, and install policy exists before any
      install/open/download/restore automation.
- [ ] Native Action / Download / Install Policy v0 has been reviewed for the
      proposed lane and action class.
- [ ] No malware safety claim, rights-clearance claim, or executable trust
      claim is made without later evidence and policy.
- [ ] Download policy has been reviewed.
- [ ] Local cache and privacy policy has been reviewed.
- [ ] Relay integration is explicitly in or out of scope.
- [ ] Live backend handoff is explicitly in or out of scope.
- [ ] No private data is consumed by default.
- [ ] No engine internals are consumed as the normal client boundary.
- [ ] No Rust FFI or runtime wiring is assumed.
- [ ] No production readiness, executable trust, or production signature claim
      is made.

## Optional Future Checks

- [ ] Snapshot checksum verification behavior is tested on the target OS.
- [ ] Future signature verification behavior has a key-management policy.
- [ ] Local cache can be cleared and inspected by the user.
- [ ] Relay sidecar threat model exists if relay integration is in scope.
- [ ] Live backend capability flags are checked before any network use.

## Signoff

- Reviewer:
- Date:
- Native lane:
- Approved scope:
- Explicit exclusions:
- Rollback/disable procedure:

Unsigned checklists are not implementation approval.
