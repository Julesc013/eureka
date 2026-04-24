# Local Development Mode

`local_dev` is the trusted-operator mode for Eureka's current stdlib web/API
backend.

It preserves the existing local demos and allows caller-provided local path
parameters. Use it only on a trusted local machine.

## Run

Local development remains the default:

```powershell
python scripts/demo_web_workbench.py
python scripts/demo_http_api.py status
```

It can also be selected explicitly:

```powershell
python scripts/demo_web_workbench.py --mode local_dev
python scripts/demo_http_api.py --mode local_dev status
```

## Allowed Local Controls

In `local_dev`, existing demos may still use:

- `index_path`
- `run_store_root`
- `task_store_root`
- `memory_store_root`
- `store_root`
- `bundle_path`

These controls are intentionally convenient for local bootstrap work. They are
not safe as public URL parameters and are blocked by `public_alpha` mode.

## Scope

Local development mode is not a hosted product mode. It does not imply auth,
HTTPS/TLS, production process management, multi-user storage, background
workers, or public deployment readiness.
