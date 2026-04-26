# Planner Gap Priorities

Old-Platform Software Planner Pack v0 reduces the current Search Usefulness
Audit planner counts to `query_interpretation_gap=21` and `planner_gap=24`.
The remaining planner gaps are now narrower than source coverage and
compatibility evidence gaps.

Planner work should follow the source capability model so the planner can target source-backed possibilities instead of inventing answers.

## Priority Areas

Implemented in Old-Platform Software Planner Pack v0:

1. OS alias graph for the bounded old-platform wedge
2. Windows NT marketing names for Windows 7, XP, and 2000
3. platform-vs-target distinction for app/software queries
4. latest-compatible release intent
5. driver/hardware/OS intent
6. vague identity intent with uncertainty notes
7. member/container discovery hints
8. app-vs-operating-system-media suppression

Remaining planner priorities:

1. unsupported/nonsense query classification
2. source-package/source-tarball distinction
3. web-archive/dead-link intent
4. manual/documentation subtypes beyond current bounded hints
5. future parity against Rust query-planner candidates

## OS Alias Graph

The planner needs deterministic aliases for:

- Windows 98 / Win9x
- Windows 2000 / NT 5.0
- Windows XP / NT 5.1
- Windows Vista / NT 6.0
- Windows 7 / NT 6.1
- Mac OS 9
- PowerPC Mac OS X 10.4

Aliases now produce structured constraints, not fuzzy matches. Future planner
work may expand the alias graph, but it must remain deterministic.

## Platform vs Target Distinction

"Windows 7 apps" is not a request for Windows 7 install media. It is a request for software compatible with Windows 7. The planner now preserves the target platform while keeping object type as software/application/utility/driver.

## Latest-Compatible Release Intent

Queries such as `latest Firefox before XP support ended` now carry:

- product name
- target OS/platform
- latest-before/support-drop constraint
- exclusion of modern incompatible releases
- preference for release notes or system requirements

## Driver/Hardware/OS Intent

Driver queries now carry hardware hints and target OS constraints:

- ThinkPad T42 Wi-Fi + Windows 2000
- Sound Blaster Live CT4830 + Windows 98
- ATI Rage 128 + Windows 98
- 3Com 3C905 + Windows 95

## Vague Identity Intent

Queries like `old blue FTP client for XP` preserve ambiguity. The planner extracts old-platform, function, visual clue, and candidate-object hints without pretending to know the answer.

## Article/Document-Member Intent

Article-inside-scan and member/container queries require document/member intent:

- title/topic clue
- issue/date hint
- article/page-range target
- OCR/page/member evidence preference

## App-vs-OS-Media Suppression

Planner output now explicitly excludes:

- operating system ISOs
- full support-media parents without member evidence
- generic advice pages
- modern incompatible releases

## Do Not Do

- do not add LLM planning
- do not add vector or fuzzy retrieval
- do not treat planner confidence as source truth
- do not route around missing source evidence
