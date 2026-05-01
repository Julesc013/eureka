# Integration Summary

P56 makes `site/dist/search.html` the static front door for public search.

Current mode:

- Static publication remains `implemented_static_artifact`.
- Public search remains `local_index_only`.
- Hosted backend status is `backend_unconfigured`.
- The generated search form is disabled for hosted search because no verified
  backend URL exists.
- Local runtime instructions point to the P54 wrapper commands.
- Static public data now includes search configuration and public index summary
  files for old clients and future handoff checks.

This is a publication-plane integration milestone only. It does not deploy a
backend or make GitHub Pages run Python.
