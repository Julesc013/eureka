# Security Policy

Eureka does not currently operate a public hosted service. The public-alpha
foundation is read-only and snapshot-backed, and any static publication surface
does not run the Python backend.

## Do Not Submit

Do not submit secrets, credentials, API keys, operator tokens, private local
paths, local instance state, private caches, raw local indexes, raw live source
responses, full-discovery raw logs, executable payloads, installers, or
copyrighted payload dumps in issues, pull requests, packs, examples, fixtures,
or audit evidence.

## Sensitive Reports

For sensitive security issues, prefer GitHub Security Advisories if they are
available for this repository. If no private GitHub advisory path is available,
use a private maintainer contact only if one is documented by the repository
owner. A private contact address is not yet documented and remains pending.

Public issues are acceptable for non-sensitive bugs, documentation drift,
validator failures, and reproducible safety-policy gaps that do not expose
private data or exploit details.

## Current Disabled Surfaces

The following remain disabled or unimplemented:

- public live source fanout
- downloads/uploads
- broad extraction
- executable/install actions
- accounts and telemetry
- hosted contribution intake
- model/provider calls
- production backend hosting
- native marketplace behavior

This policy must be updated before any hosted public service, live-source
capability, public mutation path, or user-account feature is enabled.

## License Boundary

The repository is source-available under a custom restricted license, not an
open-source license. Security review and issue reporting are allowed through the
official repository workflow, but the license does not authorize public
services, public forks, redistribution, model training, extraction services,
public Workbench exposure, live source fanout, downloads, uploads, or
commercial/professional/institutional use.

This file is a concise pre-product policy, not a complete vulnerability
disclosure, incident response, privacy, takedown, backup, or operations policy.
