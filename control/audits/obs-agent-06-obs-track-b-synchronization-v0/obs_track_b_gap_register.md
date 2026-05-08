# OBS to Track B Gap Register

## Missing OBS Prerequisites

- Human review decisions have not been recorded for OBS candidates, source leads, SearchNeed seeds, or WorkUnit seeds.
- Source policy decision packets have not been approved.
- Manual observation pending slots remain pending and are not observed baselines.

## Missing Track B Prerequisites

- Track B runtime consumption for OBS SearchNeed seeds is not defined.
- Track B runtime WorkUnit execution is not enabled by this audit.
- Candidate store, review queue, source cache, and evidence ledger runtime paths remain future/deferred.
- WorkUnit dry-run runner and node policy evaluator behavior remain outside this OBS audit.

## Source Policy Decisions

- Internet Archive metadata source policy remains review-required.
- Wayback/CDX/Memento metadata source policy remains review-required.
- GitHub Releases and package registry metadata policy remain future/deferred.
- Forum/community sources remain manual-only or permission-needed.
- Broad web scraping remains policy-blocked.

## Stale Queue And Packet Issues

- `.aide/context/latest-task-packet.md` still points at TRACK-B-06.
- `.aide/queue/index.yaml` was not updated by this OBS task to avoid overwriting parallel Track B state.

## Validation Warnings

- Full repo unittest discovery has known pre-existing Python/runtime/site artifact failures outside this OBS task.
- AIDE Lite commands that depend on the unavailable `py` launcher or Python 3.10+ `Path.write_text(newline=...)` behavior are expected to warn in this environment.
