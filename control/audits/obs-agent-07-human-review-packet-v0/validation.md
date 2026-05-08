# OBS-AGENT-07 Validation

## Scope

- Built a repo-local human review packet for OBS candidates, SearchNeed seed drafts, WorkUnit seed drafts, source-policy items, and OBS/Track B dependency items.
- No human decisions were filled in.
- No source access was approved.
- No runtime SearchNeed or WorkUnit records were created.
- No WorkUnits were executed.
- No observed baselines, accepted evidence, master-index mutations, live probes, API calls, browsers, scraping, crawling, downloads, uploads, accounts, telemetry, or product runtime changes were introduced.

## Targeted Commands

- `git diff --check`: PASS
- `python -m json.tool` for OBS-07 policy, manifest, packet JSON, and audit report: PASS
- `python scripts/build_obs_human_review_packet.py --list-inputs`: PASS
- `python scripts/build_obs_human_review_packet.py --check`: PASS
- `python scripts/validate_obs_human_review_packet.py`: PASS
- `python scripts/summarize_obs_human_review_packet.py`: PASS
- `python -m unittest tests.operations.test_obs_human_review_packet`: PASS

## Broader Validation Notes

- Adjacent OBS validators, Track B node validators, architecture boundary checks, and `python3 scripts/validate_track_a_contracts.py` pass.
- `python scripts/validate_track_a_contracts.py` fails under Python 3.8 because it uses `tuple[...]`; `python3` passes.
- `python -m unittest discover -s tests -t .` timed out after 180 seconds and deleted tracked `site/dist` outputs; `site/dist` was restored immediately.
- The `py` launcher is unavailable, so AIDE Lite commands were mapped to `python3` where possible.
- AIDE Lite `doctor`, `validate`, `eval list`, and `adapter validate` pass. AIDE Lite `verify` returns WARN with zero errors because the task packet is stale to TRACK-B-06. AIDE Lite `test`, `selftest`, `eval run`, and `review-pack` fail under Python 3.9 because `Path.write_text(newline=...)` is unsupported in this environment.
