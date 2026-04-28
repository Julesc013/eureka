# LIVE_ALPHA_00 Static Public Site Pack

`public_site/` is a committed static public site pack for Eureka live-alpha
preparation. It is plain HTML plus CSS and can be reviewed locally by opening
`index.html`.

This pack is static only. The GitHub Pages workflow can upload this directory
after validation, but the directory itself does not add backend hosting,
configure DNS, fetch external data, run live source probes, scrape external
systems, or start a server.

Validate it with:

```bash
python scripts/validate_public_static_site.py
python scripts/validate_public_static_site.py --json
python scripts/check_github_pages_static_artifact.py
```

The content intentionally describes Eureka as a Python reference backend
prototype, not production. External baselines remain pending/manual, source
placeholders remain placeholders, and live-alpha backend hosting remains future
work.
