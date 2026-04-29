# Install Handoff Contract

Install Handoff Contract v0 defines the future meaning of install handoff
without implementing it.

Install handoff is user-initiated delegation after evidence display. It is not
silent installation, not package-manager mutation, not privilege escalation,
and not executable safety.

## Future Semantics

A future native client may eventually offer install handoff only after policy,
implementation, and tests exist. Handoff may mean opening a downloaded artifact
with the operating system, delegating to a package manager, opening an emulator
or VM workflow, or presenting a restore manifest for user review.

Every handoff must be explicit and user-initiated.

## Prohibited In V0

The following are not implemented:

- silent install
- automatic execution
- privileged install
- package-manager mutation
- destructive restore
- writes to system paths
- installer launch
- uninstall or rollback automation
- emulator or VM launch
- executable download

## Required Future Preflight

Before any future handoff, the client must show:

- target and representation identity
- source id, source family, and source label
- evidence and provenance summary
- compatibility caveats
- rights/access label or unknown state
- hash/checksum availability and value when present
- signature state when present
- executable-risk warning
- malware scanning status
- rollback/uninstall status

The user must explicitly confirm after seeing this preflight.

## Rollback And Uninstall

Rollback and uninstall are not guaranteed. A future client must say when no
recipe exists. A restore manifest is an explanation or plan until later policy
and implementation prove otherwise.

## Package Managers

Package-manager handoff is future. It must not silently change package-manager
state. It must present source, version, command or package identity, rights
posture, compatibility caveats, and expected system changes before user
confirmation.

## Emulator And VM Handoff

Emulator or VM handoff is future. It must not assume firmware, operating-system
media, license rights, drivers, or executable safety. It must be governed by
rights/access and executable-risk policies.

## Not Implemented

This contract does not implement a native client, installer, package-manager
integration, emulator workflow, VM workflow, restore engine, rollback engine,
download surface, malware scanner, rights-clearance workflow, or relay runtime.
