# Backend Configuration Status

Current status: `backend_unconfigured`.

No verified hosted backend URL exists in the repo evidence reviewed for P56.
P54 added a local deployable wrapper, but no operator deployment URL, run ID,
or hosted verification evidence has been recorded.

Because the backend is unconfigured:

- hosted form submission is disabled;
- `hosted_backend_url` is `null`;
- `hosted_backend_verified` is `false`;
- static pages show local runtime instructions instead of live hosted search;
- hosted deployment remains operator-gated.

Future operator work must record the deployed URL, commit SHA, environment, and
verification checks before this status can change.
