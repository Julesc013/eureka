# Deep Extraction Runtime Plan

P105 plans a future Deep Extraction Runtime v0 without implementing it.

Deep extraction is the future mechanism for approved local fixtures or reviewed
operator-provided containers to produce metadata/member/manifest/text summaries
and candidate effects under strict sandbox/resource limits. It is not production
extraction, arbitrary archive unpacking, arbitrary local file scanning, URL
fetching, package installation, malware scanning, rights clearance, OCR runtime,
transcription runtime, public-search integration, page integration, connector
integration, pack-import integration, or mutation.

## Readiness Gates

Current readiness is `blocked_resource_limit_policy_missing`.

The Deep Extraction Contract v0 and synthetic examples exist. Runtime
implementation remains blocked because concrete resource limits and
sandbox/operator approval are not recorded.

Required gates:

- sandbox policy approved
- resource limits approved
- privacy/path/secret policy approved
- executable payload policy approved
- OCR/transcription boundary approved
- pack import boundary approved
- source-cache/evidence/candidate boundary approved
- public-search/page boundary approved
- operator approval

## Why Runtime Is Not Implemented

Runtime extraction would require opening or inspecting local payloads. P105 does
not add that behavior. It creates planning docs, inventory, a validator, and
tests only.

## Sandbox And Resource Requirements

Future runtime must disable network and execution, scope filesystem access,
create and clean a temporary workspace, enforce depth/member/size/time/text
limits, guard decompression bombs, reject path traversal, and reject symlinks or
hardlinks. Operator-approved values are still required.

## Privacy And Payload Safety

Private paths, path traversal, home/user paths, private cache roots, secrets,
private URLs, IP/account/user identifiers, raw private queries, raw payload
dumps, raw copyrighted text dumps, executable payloads, installers, scripts,
macros, package managers, emulators, and VMs remain blocked.

OCR and transcription are future hooks only. They are not truth and are disabled
by default.

## Approved Input Model

Future allowed inputs are repo-local synthetic examples, purpose-built fixture
containers, explicit operator-approved local fixture paths, and reviewed future
pack/source/page candidates. Public request parameters must never select paths,
URLs, stores, source roots, or databases.

## Pipeline And Containers

Future flow: validate request, enforce policy, create sandbox workspace, detect
container, run metadata-first tiers, build a report and candidate effects, clean
workspace, and stop before mutation.

Containers are metadata-first: archives, ISO, disk images, installers, package
archives, wheels, sdists, npm tarballs, WARC/WACZ, PDFs, scanned volumes, source
bundles, repository snapshots, and unknown containers get no execution, install,
source-code safety claim, malware safety claim, or payload extraction until
approval.

## Output And Boundaries

Reports may include request identity, target identity, tiers attempted/skipped,
container/member/manifest/text summaries, OCR/transcription summaries, safety
and privacy decisions, rights/risk labels, warnings/errors, and candidate
effects. Candidate effects are not writes. Reports are not accepted truth.

No source cache, evidence ledger, candidate index, public index, local index, or
master index mutation is allowed. Public search, page runtime, pack import, and
connector runtime do not call extraction.

## Security And Abuse

Risks include archive bombs, zip-slip, symlinks, nested archives, malicious
installers, lifecycle scripts, macros, huge text/OCR inputs, private leakage, URL
smuggling, public extraction-on-demand abuse, connector-triggered abuse,
pack-import abuse, retry storms, and sandbox escape. Future runtime needs an
operator kill switch.

## Validator

Run:

- `python scripts/validate_deep_extraction_runtime_plan.py`
- `python scripts/validate_deep_extraction_runtime_plan.py --json`

The validator is stdlib-only and checks planning artifacts and hard no-runtime
booleans.

## Next Steps

Recommended next branch: P106 Search Result Explanation Runtime Planning v0 only
after public search runtime gate.

