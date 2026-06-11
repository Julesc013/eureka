# Commands

Run all queries through JSON:

```text
python scripts/run_local_e2e_search_demo.py --all --profile json_v0
```

Run all queries through text:

```text
python scripts/run_local_e2e_search_demo.py --all --profile text_v0
```

Run one query through basic HTML:

```text
python scripts/run_local_e2e_search_demo.py --query "old blue FTP client for XP" --profile html_basic_v0
```

Run one query through snapshot:

```text
python scripts/run_local_e2e_search_demo.py --query "driver for Win98" --profile snapshot_v0
```

Regenerate deterministic fixture outputs:

```text
python scripts/run_local_e2e_search_demo.py --write-fixtures
```

Focused tests:

```text
python -m unittest tests.evals.test_local_e2e_search_demo tests.runtime.test_surface_local_e2e_demo
```

