# Architecture Checks

## Tools Found

- `scripts/check_architecture_boundaries.py`
- `tests/architecture/test_check_architecture_boundaries.py`
- `AGENTS.md`
- `docs/architecture/**`
- `control/inventory/tests/command_matrix.json`
- `docs/operations/TEST_AND_EVAL_LANES.md`

## Safe Validation Result

- `py -3 scripts/check_architecture_boundaries.py`: PASS.
- Result detail: checked 692 Python files; no architecture-boundary violations.

## Future Wrapper Plan

Future wrapper ID: `eureka.validate.architecture`.

Proposed behavior:

- Invoke `scripts/check_architecture_boundaries.py` only after a reviewed task authorizes wrapper execution.
- Capture structured output under the active `.aide/queue/<TASK-ID>/evidence/`.
- Preserve the script as the authoritative architecture check until a later task proves a replacement with evidence.

## Preservation Requirement

Q56 did not modify architecture validators, docs, tests, or dependency boundary rules. Future AIDE wrappers must call or report against the existing architecture check before any migration is considered.
