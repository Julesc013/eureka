# Root Cause

## Failing Commands

- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`

Both fail before repair with:

```text
NameError: name 'core' is not defined
```

The traceback reaches:

```text
collect_verification_findings -> gateway_status_checks ->
import_gateway_status_module -> importlib.import_module("core.gateway.gateway_status")
```

and then fails while Python executes the temporary fixture file:

```text
...\Temp\...\core\gateway\__init__.py, line 1
```

## Why `core.gateway.__init__` Is Referenced

`run_selftest()` creates a temporary repo with `_write_minimal_repo()`. The
verification path includes Q19 Gateway checks, and those checks import
`core.gateway.gateway_status` from the temporary repo so they can confirm the
offline Gateway status helpers disable provider/model calls.

## Why It Fails In Eureka

The Q25 safe importer intentionally skips optional broad roots such as
`core/**`. In Eureka, `repo_root_from_script()` points at this target repo, not
the full AIDE source repo, so `_write_minimal_repo()` cannot copy the optional
`core/gateway/**` and `core/providers/**` Python helper files.

When those optional source files are missing, `_write_minimal_repo()` writes a
generic fallback text block for every missing Q19/Q20 file. That fallback is
acceptable for YAML/Markdown metadata, but it is invalid for `.py` modules. For
example, a missing `core/gateway/__init__.py` receives text beginning with a
`schema_version: core/gateway/__init__.py` style line. Python interprets that as
code and raises `NameError: name 'core' is not defined` during import.

## Exported Test Expectation

The exported tests are meaningful: they expect the portable selftest fixture to
exercise Gateway and Provider offline metadata checks. The failure is not that
Eureka lacks product Gateway/provider code; it is that the portable selftest
fixture's fallback writes invalid Python when optional AIDE source modules are
not imported.

## Why Broad `core/**` Import Is Not Acceptable

Q26 verified that safe import must skip broad source roots by default. Copying
AIDE `core/**` into Eureka would broaden target scope, pollute the target repo
with source AIDE skeletons, and violate this task's forbidden paths. The repair
must keep any helper package inside the selftest temporary fixture only.

## Minimal Correct Fallback

The correct repair is to make `_write_minimal_repo()` write valid, offline,
minimal Python helpers for missing optional Q19/Q20 `.py` files inside the
temporary fixture. These helpers must be enough for the existing Gateway and
Provider metadata checks to run, while preserving safe import scope and avoiding
any committed `core/**` files in Eureka.
