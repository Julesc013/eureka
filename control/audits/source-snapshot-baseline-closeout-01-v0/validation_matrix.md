# Validation Matrix

- `python scripts/eureka_test_select.py --changed --failed-first --json`: pass
- `python scripts/validate_source_action_kernel.py`: pass
- `python scripts/validate_source_wave.py`: pass
- `python scripts/validate_snapshot_relay.py`: pass
- `python scripts/check_architecture_boundaries.py`: pass
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: pass
- `python .aide/scripts/aide_lite.py doctor`: pass
- `python .aide/scripts/aide_lite.py validate`: pass_with_warnings
- `python -m unittest discover -s tests -t .`: fail
