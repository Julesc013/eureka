# Validation

Planned validation commands:

```powershell
python scripts\validate_play_seed_pack.py
python scripts\eureka_seed_play_demo.py --instance ../instances/default --dry-run --json
python scripts\eureka_play_smoke.py --instance ../instances/default --operator-token local-dev-token --json
python -m unittest tests.runtime.test_play_seed_pack
python -m unittest tests.operations.test_play_session
python -m unittest tests.operations.test_play_smoke
python scripts\check_architecture_boundaries.py
python scripts\check_generated_artifact_cleanliness.py --check --json
```

Full discovery remains optional for PLAY-00 because the task adds fixture data,
scripts, docs, tests, and control evidence without changing runtime packages.
