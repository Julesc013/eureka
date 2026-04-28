# Static Site Source Tree

`site/` is the governed stdlib-only source and generator tree for Eureka's
static public site.

Current boundary:

- `site/` contains source JSON, templates, assets, and generator scripts.
- `site/dist/` is generated output from `python site/build.py`.
- `site/dist/data/` is populated by Generated Public Data Summaries v0 for
  validation against the current static publication data.
- `public_site/` remains the GitHub Pages deployment artifact for this
  milestone.

The generator uses only Python standard library modules. It does not use
Node/npm, frontend frameworks, live backend calls, live source probes, external
web APIs, scraping, browser automation, or deployment behavior.

Common commands:

```bash
python site/build.py --check
python site/build.py --json
python site/validate.py
python site/validate.py --json
```

The public data generator can also be checked directly:

```bash
python scripts/generate_public_data_summaries.py --check
```

Generated output is no-JS static HTML with relative links so it can work under
the GitHub Pages project base path `/eureka/` and a future custom-domain root
path `/`.

`site/build.py --output public_site` is intentionally refused in this milestone
so generated output cannot replace the deployable artifact by accident.

Generated public data remains static JSON only. It does not create a live API,
enable live probes, record external observations, or change deployment
behavior.
