# Action Router

The resolver should not stop at "here are some matches." It should route users
toward the most useful next action that can be justified by current evidence.

## Action Families

Important bounded action families include:

- inspect
- view or read
- fetch
- download later
- mirror
- export manifest
- save to local archive
- compare versions
- inspect provenance

High-risk actions such as installer execution or restore flows remain deferred.

Native Action / Download / Install Policy v0 governs the boundary between safe
read-only actions, bounded local fixture/manifest actions, and future risky
actions. It keeps download, mirror, install handoff, package-manager handoff,
execute, restore, uninstall, rollback, malware scanning, private upload, and
rights-clearance claims disabled until separate policy and implementation work
exists.

## Usefulness and User Cost

Eureka should rank results by more than keyword relevance. Important dimensions
include:

- intent fit
- compatibility fit
- provenance quality
- integrity evidence
- temporal fit
- actionability
- risk
- user cost

User cost matters because parent bundles, opaque container hits, and ambiguous
version traces make the user do manual detective work.

## Visible Result Lanes

The UI should eventually separate results into visible lanes rather than one
flat list.

Illustrative lanes include:

- best direct answer
- installable or usable now
- inside bundles
- official
- preservation
- community
- documentation
- mentions or traces
- absence or next steps

## Explain The Route

The resolver should be able to explain:

- why a result was ranked well
- why a parent bundle was demoted
- why a compatibility hint matters
- why an action is recommended, available, or unavailable

It should also explain when an action is blocked by policy. A future result
must not hide executable risk, missing rights/access clearance, missing hash or
signature evidence, unknown compatibility, or rollback limits behind a single
button.
