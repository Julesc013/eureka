# Delta Summary

Search Usefulness Audit Delta v1 records a meaningful but still bounded
movement after Old-Platform Source Coverage Expansion v0.

## Status Count Delta

| Status | Baseline | Current | Change |
| --- | ---: | ---: | ---: |
| covered | 5 | 5 | 0 |
| partial | 5 | 20 | +15 |
| source_gap | 41 | 28 | -13 |
| capability_gap | 11 | 9 | -2 |
| unknown | 2 | 2 | 0 |

The main movement is from source/capability gaps into source-backed partials.
No report here claims broad search completeness.

## Archive Eval Delta

| Status | Baseline | Current | Change |
| --- | ---: | ---: | ---: |
| capability_gap | 5 | 1 | -4 |
| not_satisfied | 1 | 5 | +4 |
| satisfied | 0 | 0 | 0 |

Moving from `capability_gap` to `not_satisfied` is progress because the system
now has local source/planner/evidence results for more hard tasks. It remains
unsatisfied because exact expected-result checks are still not met.

## Conclusion

Old-platform fixture expansion worked: `partial` increased by 15 and
`source_gap` decreased by 13. The next bottleneck is now sharper. Several hard
archive eval tasks have local evidence but fail exact expected-result checks,
so the next milestone should be **Hard Eval Satisfaction Pack v0** rather than
another broad source pack.

External Google and Internet Archive baselines remain pending/manual.
