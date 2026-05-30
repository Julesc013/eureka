# Validation

Focused validation run:

- `git diff --check`: pass with Windows CRLF warnings only
- `python scripts/validate_query_to_source_action_planner.py`: pass
- `python scripts/validate_public_alpha_readonly.py`: pass
- `python scripts/validate_source_action_kernel.py`: pass
- `python scripts/validate_source_wave.py`: pass
- `python scripts/validate_domain_packs.py`: pass
- `python scripts/check_architecture_boundaries.py`: pass
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: pass
- focused query planner unittest modules: pass
- public-search API regression subset: pass
- AIDE doctor, validate, test, selftest, verify, review-pack: pass

Full unittest discovery is intentionally not run inside the AI session.
