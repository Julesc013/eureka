# Action Download Install Policy

Native Action / Download / Install Policy v0 defines the first governed policy
for Eureka actions that may eventually cross from metadata inspection into
artifact handling, native-client handoff, package-manager handoff, mirroring,
or system changes.

This is policy and contract work only. It does not implement downloads,
installers, install automation, package-manager integration, native clients,
relay runtime, malware scanning, rights clearance, executable trust, or public
download surfaces.

## Action Taxonomy

Eureka actions fall into four broad classes.

| Class | Current posture | Examples | Policy posture |
| --- | --- | --- | --- |
| Safe read-only | Current, bounded | inspect, preview, read, cite, view provenance, compare, view absence report, view source | May show existing governed facts and limitations. |
| Bounded local artifact | Current, local-only | export manifest, fixture payload fetch, member preview, local artifact store | Developer-local or fixture-only. Not a public download surface. |
| Future download or mirror | Future gated | download, download member, mirror | Disabled until rights, security, checksum, and operator policies exist. |
| Future install or execute | Future gated | install handoff, package-manager handoff, emulator/VM handoff, restore, uninstall, rollback, execute | Disabled until explicit policy, implementation, and user confirmation rules exist. |

## Current Implemented Or Bounded Actions

Current Eureka behavior can safely inspect and describe already governed data.
It can show source records, evidence, compatibility caveats, absence reports,
comparison summaries, public data, static pages, snapshot seed manifests, and
bounded local fixture/member previews.

Current local developer behavior can export deterministic manifests and bounded
fixtures through existing local seams. Those are not public download
semantics, not production artifact hosting, not install handoff, and not a
license or safety statement.

Public-alpha mode keeps risky actions closed. Static Pages keeps risky actions
absent.

Public Search Result Card Contract v0 must project these rules in every future
search card. Read-only actions may appear under `actions.allowed`; downloads,
member downloads, mirrors, install handoff, package-manager handoff, emulator or
VM handoff, execution, restore, rollback, uninstall, uploads, and private-source
submission must appear only as blocked or future-gated until a later accepted
policy and implementation changes that posture.

Public Search Safety / Abuse Guard v0 applies the same posture before runtime:
public search must reject download, install, execute, upload, and related action
requests with the governed disabled-action error codes. The safety guard does
not implement download/install middleware or action execution.

## Future Gated Actions

The following actions are future and disabled until later policy plus
implementation work exists:

- download
- download member
- mirror
- install handoff
- package-manager handoff
- emulator handoff
- VM handoff
- restore manifest apply
- uninstall
- rollback
- execute
- scan for malware
- quarantine
- submit feedback
- upload local source

Future gating requires at minimum source/provenance display, rights/access
posture, hash/checksum availability, executable-risk warnings, explicit user
confirmation, privacy/local-cache review where private state is involved,
operator signoff where relevant, and tests that prove disabled defaults remain
disabled.

## Prohibited Actions

These actions remain prohibited until a later accepted policy explicitly moves
them:

- silent install
- automatic execution
- privileged install
- destructive restore
- writes to system paths
- uploading private files
- sending private inventory
- automatic local archive scanning
- telemetry by default
- bypassing rights warnings
- bypassing hash warnings

No current surface may expose these as available behavior.

## Install Handoff Versus Install Automation

Install handoff means a future user-initiated delegation to a system opener,
installer, emulator, VM, or package manager after the client shows evidence,
provenance, hashes, rights/access posture, compatibility caveats, and risk
warnings.

Install automation means Eureka silently or programmatically installs,
executes, modifies package-manager state, escalates privilege, or writes to
system paths. Install automation is not implemented and remains prohibited.

Package-manager handoff is also future. It is not direct installation and does
not permit silent mutation of package-manager state.

## Required Labels And Evidence

Before any future risky handoff, a client must show:

- source id, source family, and source label
- target or resolved resource id
- representation id or member path when applicable
- evidence and provenance summary
- compatibility summary when present
- rights/access label, including unknown when unknown
- hash or checksum availability
- signature status when present
- fixture, recorded fixture, placeholder, or live-source status

Unknown is a valid label. Unknown must not be converted into clearance,
safety, authenticity, or compatibility.

## User Confirmation

Safe read-only actions do not require special confirmation.

Bounded local writes must confirm the local destination and state that the
output is a local developer artifact.

Future downloads, mirrors, installs, executes, restores, uninstalls, rollbacks,
or package-manager handoffs must require explicit user confirmation after the
client shows source, rights/access posture, hash/signature state, compatibility
caveats, executable-risk warning, and rollback limitations.

## Public-Alpha And Static Restrictions

Public-alpha defaults are read-only and metadata-first. Downloads, fixture byte
fetch, installer handoff, package-manager handoff, mirror, execute, private
upload, malware scanning, and rights-clearance claims are disabled.

GitHub Pages/static publication may show policy, metadata, public data,
snapshots, checksums, and limitations. It must not host a download/install
surface, executable mirror, package-manager integration, app-store workflow, or
live action endpoint.

## Native, Snapshot, And Relay Requirements

Future native clients must implement this policy before any download, install
handoff, package-manager handoff, mirror, execute, restore, uninstall, or
rollback behavior.

Native Local Cache / Privacy Policy v0 must also be followed before any private
cache, private upload, diagnostics upload, source credential handling, local
archive scanning, account state, telemetry, or cloud sync behavior.

Snapshot consumers may inspect, read, preview, and verify checksums. Snapshot
consumption is not permission to download, install, execute, mirror, or restore
software.

Relay surfaces remain public/read-only by default. Insecure old-client
transports must not expose private data, write/admin controls, download,
install, execute, mirror, live-probe, or upload behavior.

Relay Prototype Planning v0 keeps the first future relay prototype inside that
rule: local static HTTP, localhost-only by default, read-only, static, and no
downloads, mirrors, installers, executable launch, write/admin routes, live
backend proxying, or live probes.

## Malware And Rights Disclaimers

No malware safety claim exists. No scanner, sandbox, quarantine workflow, or
clean/safe executable verdict exists in v0.

No rights clearance claim exists. Source metadata, public indexing, fixture
presence, checksum presence, or snapshot inclusion does not prove permission to
distribute, mirror, download, install, or execute an artifact.

Hashes verify identity or integrity only when the hash source is trusted. A
hash does not prove safety, legality, authenticity, or compatibility.

## Not Implemented

This policy does not implement:

- downloads
- installers
- install automation
- package-manager integration
- native clients
- GUI behavior
- FFI
- relay runtime
- public download pages
- executable mirrors
- real malware scanning
- quarantine
- rights clearance
- live source probes
- production readiness

<!-- P85-COMPATIBILITY-AWARE-RANKING-START -->
## P85 Compatibility-Aware Ranking Contract v0

P85 adds a contract-only compatibility-aware ranking layer. It defines public-safe target profiles, compatibility factors, cautious explanations, no installability without evidence, no emulator/VM or package-manager launch, no runtime ranking, no public search order change, no hidden suppression, and no index/cache/ledger/candidate/master-index mutation.
<!-- P85-COMPATIBILITY-AWARE-RANKING-END -->
