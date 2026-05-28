# Static Site Source Tree

`site/` contains stdlib-only static site source, templates, data, assets, and
generation code. `site/dist/` is the generated static artifact tree.

The static site is not the Python backend. It does not provide hosted search,
live source fanout, downloads, uploads, broad extraction, accounts, telemetry,
model/provider calls, or production API behavior.

Common checks:

```powershell
python site/build.py --check
python site/build.py --json
python site/validate.py
python site/validate.py --json
python scripts/check_github_pages_static_artifact.py --json
```

Generated output should remain no-JS/static, base-path portable, and honest
about backend availability. A generated static artifact or GitHub Pages
workflow is not by itself a deployment success or public launch claim.
