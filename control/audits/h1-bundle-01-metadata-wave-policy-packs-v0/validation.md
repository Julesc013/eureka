# Validation

Validation commands run for H1-BUNDLE-01:

- `git diff --check`: PASS
- `python scripts/validate_h1_metadata_wave_policy_packs.py`: PASS
- `python scripts/summarize_h1_metadata_wave_sources.py --check`: PASS
- `python -m unittest tests.operations.test_h1_metadata_wave_policy_packs`: PASS
- `python -m unittest tests.operations.test_h1_metadata_wave_summary`: PASS
- `python -m unittest discover -s tests -t .`: PASS
- `python scripts/check_architecture_boundaries.py`: PASS
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with warnings for existing missing optional review-packet refs
- `py -3 .aide/scripts/aide_lite.py test`: PASS
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, zero errors
- `py -3 .aide/scripts/aide_lite.py eval list`: PASS
- `py -3 .aide/scripts/aide_lite.py eval run`: PASS
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS with verifier WARN
- `py -3 .aide/scripts/aide_lite.py adapter validate`: PASS

Existing H0/IA/core validators were also run. The IA readiness validator passed after the H1 task packet explicitly named the H0 prerequisite chain.
