# Planner Gap Priorities

Planner and query interpretation gaps are nearly as dominant as source gaps: `query_interpretation_gap=46` and `planner_gap=45`.

Planner work should follow the source capability model so the planner can target source-backed possibilities instead of inventing answers.

## Priority Areas

1. OS alias graph
2. Windows NT marketing names
3. platform-vs-target distinction
4. latest-compatible release intent
5. driver/hardware/OS intent
6. vague identity intent
7. article/document-member intent
8. app-vs-operating-system-media suppression

## OS Alias Graph

The planner needs deterministic aliases for:

- Windows 98 / Win9x
- Windows 2000 / NT 5.0
- Windows XP / NT 5.1
- Windows Vista / NT 6.0
- Windows 7 / NT 6.1
- Mac OS 9
- PowerPC Mac OS X 10.4

Aliases should produce structured constraints, not fuzzy matches.

## Platform vs Target Distinction

"Windows 7 apps" is not a request for Windows 7 install media. It is a request for software compatible with Windows 7. The planner must preserve the target platform while keeping object type as software/application/utility/driver.

## Latest-Compatible Release Intent

Queries such as `latest Firefox before XP support ended` need:

- product name
- target OS/platform
- latest-before/support-drop constraint
- exclusion of modern incompatible releases
- preference for release notes or system requirements

## Driver/Hardware/OS Intent

Driver queries need hardware hints and target OS constraints:

- ThinkPad T42 Wi-Fi + Windows 2000
- Sound Blaster Live CT4830 + Windows 98
- ATI Rage 128 + Windows 98
- 3Com 3C905 + Windows 95

## Vague Identity Intent

Queries like `old blue FTP client for XP` should preserve ambiguity. The planner can extract old-platform, function, visual clue, and candidate-object hints without pretending to know the answer.

## Article/Document-Member Intent

Article-inside-scan queries require document/member intent:

- title/topic clue
- issue/date hint
- article/page-range target
- OCR/page/member evidence preference

## App-vs-OS-Media Suppression

Planner output should explicitly exclude:

- operating system ISOs
- full support-media parents without member evidence
- generic advice pages
- modern incompatible releases

## Do Not Do

- do not add LLM planning
- do not add vector or fuzzy retrieval
- do not treat planner confidence as source truth
- do not route around missing source evidence
