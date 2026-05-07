# Compact Prompt

Repair Eureka's imported AIDE Lite `test` and `selftest` failure by fixing the
target-local selftest fixture fallback in `.aide/scripts/aide_lite.py`.

The failure is the Q26-recorded `core.gateway.__init__` temp-fixture issue.
Do not copy AIDE `core/**` into Eureka, do not change Eureka product code, do
not mutate AIDE or Dominium, and do not make provider/model/network calls.

Run and record doctor, validate, test, selftest, verify, eval, adapter
validation, packet generation, estimate, architecture boundaries, diff check,
ignore check, and a strict secret scan.
