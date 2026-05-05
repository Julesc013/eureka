# Operator Actions Required

- Enable or repair the static host for the configured GitHub Pages URL, then rerun python scripts/verify_public_hosted_deployment.py --static-url <url> --json.
- Deploy the hosted public search wrapper separately, with safe environment flags, then record EUREKA_PUBLIC_BACKEND_URL or inventory base_url and rerun the verifier.
- Configure and evidence edge or application rate limits before any hosted public-search claim.
- Record TLS, CORS, cache, and security header evidence from the deployed static and backend hosts.
- Update static search handoff only after backend verification, rebuild site/dist, and verify the handoff points to the verified backend URL.
- Keep live connectors, downloads, uploads, accounts, telemetry, arbitrary URL fetch, and index/cache/ledger mutation disabled.
