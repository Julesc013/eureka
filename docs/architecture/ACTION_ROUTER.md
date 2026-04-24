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
