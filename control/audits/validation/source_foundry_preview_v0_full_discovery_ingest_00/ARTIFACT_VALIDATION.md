# Artifact Validation

Run ID:

```text
source_foundry_preview_v0_post_historical_repair_02
```

## Required Artifacts

| Artifact | Status | SHA-256 |
| --- | --- | --- |
| `../eureka-test-runs/source_foundry_preview_v0_post_historical_repair_02/full_unittest_summary.json` | present | `c7474aed72fb8ba598a167020099843b28ed464d74c7cd762ccd3d109a0430be` |
| `../eureka-test-runs/source_foundry_preview_v0_post_historical_repair_02/failed_tests.txt` | present, empty | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `../eureka-test-runs/source_foundry_preview_v0_post_historical_repair_02/failure_families.json` | present, empty families | `19e8eb933d7f1f0d84e1bede9590bc18b7ca87d779db49c832b3a2a973a5076b` |

## Optional Raw Artifacts

| Artifact | Status | SHA-256 |
| --- | --- | --- |
| `full_unittest_stdout.txt` | present | `56ec8f116f6dd79c29bcee7bd822d55c8d1ad630e5860a0c9fa34409e44584b4` |
| `full_unittest_stderr.txt` | present | `d1f816bfc35a3b09b8a001fd4faff2c94a424e236ebdaeeb1175509f749d0692` |
| `environment.json` | present | `a2e9634a6150a82ab99b4af7241416aac2219fc5eb88bce15701b923a190326d` |
| `status.json` | present | `16a3e9da635875edb7d8e4e9bcaca84c74b97734103de7f86f6b510669a5008b` |

## Validation

- Run ID matches the handoff.
- Tested commit is `bad6bf6d954cc4f497079e97cab946b11dde404d`.
- The tested commit is a docs-only descendant of the repair commit
  `1ceeed045b7fb8afa24485545525aeeaadb64507`.
- Expected test count was 5,793.
- Actual test count was 5,793.
- Exit code was 0.
- Failure count was 0.
- Error count was 0.
- `failed_tests.txt` is empty.
- `failure_families.json` contains no active failure families.
- The prior red checkpoint run ID was not overwritten.

