# Compatibility Evidence Priorities

Compatibility evidence is the main actionability multiplier for the primary wedge. Search Usefulness Audit v0 reports `compatibility_evidence_gap=25`.

Status: Compatibility Evidence Pack v0 is implemented as the first bounded
source-backed evidence seam. It extracts current fixture-backed evidence from
metadata, member paths, README text, and compatibility notes. It does not create
a compatibility oracle, execute software, verify installers, call live sources,
or replace unknown compatibility outcomes.

## First Platform Set

The first compatibility evidence pack should cover:

- Windows 98
- Windows 2000
- Windows XP
- Windows Vista
- Windows 7 / NT 6.1
- x86 and x64 distinctions where source evidence supports them

V0 currently proves this pattern on the committed fixture corpus, especially
Windows 7 / NT 6.1, Windows XP / NT 5.1, and Windows 2000 / NT 5.0 evidence.
Windows 98, Windows 95, Vista-depth evidence, and broader architecture coverage
remain source-coverage follow-up work.

## Object Distinctions

Compatibility evidence must distinguish:

- installer
- portable app
- driver
- runtime dependency
- source package
- documentation/manual

Drivers are especially sensitive because hardware and OS evidence both matter.

## Evidence Types

Evidence should be typed as:

- official system requirements
- release notes
- readme/manual
- package metadata
- community report
- inferred/unknown

`unknown` compatibility is a first-class outcome. Unknown is better than pretending an old-platform target is supported.

## Confidence Levels

Suggested v0 confidence values:

- `source_confirmed`: direct source evidence says compatible
- `source_constrained`: source evidence strongly narrows the platform but does not fully prove compatibility
- `community_reported`: non-official evidence suggests compatibility
- `inferred_low_confidence`: weak inference only; should not be used as truth
- `unknown`: no reliable compatibility evidence
- `incompatible`: source evidence says unsupported

## Tests To Add First

- Windows 7 / NT 6.1 alias compatibility tests: implemented for fixture-backed
  evidence
- Windows XP evidence tests: implemented for current fixture evidence
- driver hardware + OS evidence tests: implemented for the ThinkPad T42
  Windows 2000 fixture member
- unknown compatibility rendering tests: implemented for unrelated records
- no compatibility oracle from guesses: implemented at v0 scope

## Do Not Do

- do not execute installers
- do not infer compatibility as objective truth
- do not collapse unknown into compatible
- do not build a full compatibility oracle
- do not let user strategy mutate compatibility evidence
