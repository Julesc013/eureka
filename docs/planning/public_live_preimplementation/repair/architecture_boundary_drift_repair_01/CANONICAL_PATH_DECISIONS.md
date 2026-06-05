# Canonical Path Decisions

## Runtime Paths

No runtime modules were moved.

The only R0 seam file implicated by the current label was:

```text
runtime/source/observation/internet_archive_live_transport.py
```

The audit findings in that file were `User-Agent` false-positive candidates, not
actual task/control vocabulary leakage.

## Control Evidence

The following control evidence was updated:

```text
control/policies/runtime_architecture_leakage_allowlist.json
control/inventory/legacy_runtime_leakage_remediation_result.json
control/inventory/legacy_runtime_leakage_remaining_allowlist.json
control/audits/r0-remediation-legacy-leakage-01-v0/remediation_report.json
```

## Tests And Validators

The following validator/test files were updated:

```text
tools/validators/validate_legacy_runtime_leakage_remediation.py
tools/validators/validate_repo_structure_canon.py
tests/scripts/test_validate_repo_structure_canon.py
```

## No Broad Path Work

No compatibility shims were moved, no new canonical roots were introduced, and no
public/gateway/surface shortcut was added.

