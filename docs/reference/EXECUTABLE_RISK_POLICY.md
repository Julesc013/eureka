# Executable Risk Policy

Executable Risk Policy v0 records how Eureka must talk about executable,
installer, script, driver, archive member, and package-manager risks before
any future download or install handoff exists.

This is policy only. Eureka does not scan executables, run malware detection,
quarantine files, execute artifacts, install software, or claim executable
safety.

## Core Rules

- Executables and installers may be risky.
- Hashes verify identity or integrity only; hashes do not prove safety.
- Signatures, if present later, require a verification and trust policy before
  they can support authenticity claims.
- Compatibility evidence is not safety evidence.
- Source metadata is not rights clearance.
- Fixture `.exe.txt` files are text fixtures, not executable programs.
- Public-alpha must not execute, install, download, or mirror executable
  artifacts.
- Static Pages must not expose an executable download or install surface.

Public Search Result Card Contract v0 carries this posture through the `risk`
block. Cards may report `metadata_only`, `executable_unknown`,
`executable_present`, or `not_applicable`, but they must not claim malware
safety, must not make executable artifacts downloadable, and must not expose
execution or installer handoff as an allowed v0 action.

## Required Future Warnings

Before any future native-client handoff involving an executable-like artifact,
the client must show warnings for:

- executable risk unknown
- malware scanning not available unless a future scanner actually exists
- hash identity is not safety
- signature status may be absent, unknown, or placeholder-only
- compatibility is not guaranteed
- install, rollback, and uninstall behavior may not be available
- rights/access posture may be unknown

Warnings must appear before handoff, not after.

## Hashes And Signatures

A checksum can help detect accidental corruption or identity mismatch. It does
not prove that a file is safe to execute.

A signature can only support authenticity after a future policy defines key
management, trusted key distribution, revocation/rotation, release provenance,
and client-side verification behavior.

Snapshot Format v0 signatures are placeholders only. They do not create a
production trust chain.

## Fixtures

The current repo may contain text fixtures with names that resemble executable
or installer artifacts. These fixtures are text-safe records used for
deterministic tests and documentation. They are not executable distribution and
must not be presented as downloadable or runnable software.

## Future Scanner Work

Future malware scanning, sandboxing, reputation checks, or quarantine behavior
would require a separate policy, implementation, tests, and operator/user
controls.

No malware safety claim exists in v0.
