# Full Discovery Evidence

Current status: `PASS`

External command run by the operator:

```powershell
python scripts/eureka_test_gate.py --gate promotion_gate --watch --clean
```

Compact result:

- gate: `promotion_gate`
- head: `8f02824e0fb87431e104a63516af74089fbb461d`
- tests_run: 5081
- failures: 0
- errors: 0
- exit_code: 0
- duration_seconds: 2926.539254

The compact summary still records an expected refusal-path trace for forbidden
output roots. It is nonblocking because unittest completed with status PASS,
exit code 0, failures 0, and errors 0.
