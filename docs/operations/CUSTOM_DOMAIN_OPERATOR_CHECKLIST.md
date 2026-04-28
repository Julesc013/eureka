# Custom Domain Operator Checklist

Status: unsigned/future.

This checklist is for a later operator task. It is not permission to configure
DNS or add a `CNAME` file now.

- [ ] Choose the intended domain and record the decision in publication
  inventory.
- [ ] Verify domain ownership in the hosting provider or GitHub outside this
  repo.
- [ ] Review DNS changes outside this repo.
- [ ] Decide whether a future task should add `public_site/CNAME` or configure
  the domain only through host settings.
- [ ] Run `python scripts/validate_static_host_readiness.py`.
- [ ] Run `python scripts/validate_publication_inventory.py`.
- [ ] Run `python scripts/validate_public_static_site.py`.
- [ ] Run `python scripts/check_github_pages_static_artifact.py`.
- [ ] Confirm static internal links remain relative and work under `/eureka/`
  and `/`.
- [ ] Confirm no backend hosting is implied.
- [ ] Confirm no live source probes are enabled.
- [ ] Confirm no production-ready or deployment-success claim is introduced.
- [ ] Confirm rollback steps for removing host binding and DNS are documented.
- [ ] Record operator signoff and date.

Do not proceed if any item is unchecked.
