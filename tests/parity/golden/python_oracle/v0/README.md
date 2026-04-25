# Python Oracle Golden v0

This fixture pack captures stable JSON outputs from the current Python
reference backend for the first Rust parity lane.

Included seams:

- source registry
- query planner
- resolution runs
- local index
- resolution memory
- archive-resolution eval runner

Regenerate or check with:

```powershell
python scripts/generate_python_oracle_golden.py
python scripts/generate_python_oracle_golden.py --check
```

Unstable fields are normalized:

- timestamps: `<PYTHON_ORACLE_TIMESTAMP>`
- local index paths: `<PYTHON_ORACLE_LOCAL_INDEX_PATH>`
- local index FTS mode: `<PYTHON_ORACLE_FTS_MODE_NORMALIZED>`
- manifest commit and generation time placeholders

The archive-resolution eval outputs intentionally preserve current capability
gaps. Do not weaken hard eval fixtures to make the report look greener.
