# Bad Result Patterns

The eval runner now scores hard-task bad-result patterns deterministically.

The scoring is not production ranking. It checks whether a known bad pattern is
accepted as the primary bounded result shape.

Examples now guarded:

- OS install media is not accepted as a best app/software answer.
- Parent support CDs without member visibility are not accepted for driver
  member tasks.
- Manuals without driver artifacts are not accepted for driver artifact tasks.
- Wrong platform or wrong hardware evidence blocks driver satisfaction.
- Latest-release traces without requested platform evidence are not enough.
- Generic FTP lists without function/member evidence do not satisfy vague
  identity tasks.
- Registry advice without an artifact/tool trace does not satisfy Windows 98
  registry repair.
- Bundle-only records without members/artifacts do not satisfy direct
  application tasks.

The current run found no known bad pattern accepted as the primary result for
the five old-platform tasks. The four remaining partial tasks are blocked by
result-shape or evidence limits, not by bad-result acceptance.
