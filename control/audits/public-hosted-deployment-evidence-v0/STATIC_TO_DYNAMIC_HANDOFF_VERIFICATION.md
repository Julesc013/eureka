# Static-to-Dynamic Handoff Verification

The remote `data/search_config.json` route returned 404, so deployed handoff could not be verified. The repo-local `site/dist/data/search_config.json` remains backend-unconfigured with `hosted_backend_url: null`, `hosted_backend_verified: false`, and no fake URL claim. The static search form must point to a hosted backend only after backend verification.
