# Compatibility Evidence Priorities

Compatibility evidence is the main actionability multiplier for the primary wedge. Search Usefulness Audit v0 reports `compatibility_evidence_gap=25`.

## First Platform Set

The first compatibility evidence pack should cover:

- Windows 98
- Windows 2000
- Windows XP
- Windows Vista
- Windows 7 / NT 6.1
- x86 and x64 distinctions where source evidence supports them

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

- Windows 7 / NT 6.1 alias compatibility tests
- Windows XP support-drop evidence tests
- driver hardware + OS evidence tests
- unknown compatibility rendering tests
- no compatibility oracle from guesses

## Do Not Do

- do not execute installers
- do not infer compatibility as objective truth
- do not collapse unknown into compatible
- do not build a full compatibility oracle
- do not let user strategy mutate compatibility evidence
