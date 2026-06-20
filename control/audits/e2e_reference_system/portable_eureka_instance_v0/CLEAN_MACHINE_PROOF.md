# Clean-Machine Proof

Focused proof command:

```powershell
python -m unittest tests.e2e.test_portable_eureka_clean_machine -v
```

Observed in focused portable lane:

```text
bootstrap: pass
idempotent bootstrap: pass
doctor: pass/pass_with_warnings
core oracle: pass
Hunt: pass
replay: pass
status: pass
serve smoke: pass
```

The test uses a temporary explicit instance and removes it afterward.
