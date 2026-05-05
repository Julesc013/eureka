# Public Hosted Deployment Evidence

P77 defines how Eureka records factual evidence for a public static site and a separate hosted backend. It performs no deployment, no provider configuration, no DNS changes, no credential use, no production claim, and no product-runtime expansion.

GitHub Pages and similar static hosts are static-only. They can serve `site/dist`, `/search.html`, and generated JSON, but they do not run the Python hosted backend. The hosted backend is separate and operator-gated.

Run static evidence checks with:

```bash
python scripts/verify_public_hosted_deployment.py --from-repo-config --json
python scripts/verify_public_hosted_deployment.py --from-env --json
python scripts/verify_public_hosted_deployment.py --static-url <verified-static-url> --json
```

Run backend evidence checks only after the operator records an explicit backend URL:

```bash
python scripts/verify_public_hosted_deployment.py --backend-url <verified-backend-url> --json
python scripts/validate_public_hosted_deployment_evidence.py
```

Unverified means exactly that: no hosted backend availability claim, no public hosted search claim, and no production claim. A configured URL that returns 404 is a failed evidence result, not a success.

After backend deployment, update static handoff only with a verified backend URL, rebuild `site/dist`, and rerun the verifier. Static search must stay honest when backend evidence is missing.

Live connectors remain disabled. Public hosted search must stay `local_index_only`; it must not call external sources, accept arbitrary URL fetches, expose downloads/uploads/accounts/telemetry, or mutate indexes. The verifier and validator are evidence tools, not deployment tools. Public evidence checks must not mutate indexes.
