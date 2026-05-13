# Site Dist Test Isolation

`site/dist` is canonical generated deployment output. Ordinary tests must not write to it.

Tests that exercise the static site generator should pass `--output` with a temporary directory. This keeps generated HTML, manifests, checksums, and compatibility surfaces isolated from committed deployment artifacts.

The expected pattern is:

```python
with tempfile.TemporaryDirectory() as temp_dir:
    output = Path(temp_dir) / "site"
    subprocess.run([sys.executable, "site/build.py", "--output", str(output), "--json"], check=True)
```

After a test run, verify the boundary with:

```powershell
python scripts/check_generated_artifact_cleanliness.py --check --json
git status --short
```

If `site/dist` changes, either the test is not isolated or the canonical site output was intentionally regenerated. Intentional regeneration must be recorded with the generator and validation commands.
