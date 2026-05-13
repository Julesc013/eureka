# Git State

Before promotion:

- branch: `dev`
- HEAD: `4cde57bd1004a384d7b0c9f83f73ced209bdc742`
- `origin/dev`: `4cde57bd1004a384d7b0c9f83f73ced209bdc742`
- `origin/main`: `c5e131da12a67b86259874f6ac7145de4d2d3661`
- `origin/main...origin/dev`: `0 89`
- `dev` contained `origin/main`: true

Promotion:

- `git push origin dev`: completed; remote was already up to date.
- `git merge --ff-only origin/dev` on `main`: completed.
- `git push origin main`: completed.
- `git switch dev` and `git merge --ff-only origin/main`: completed; already up to date.

After promotion:

- `origin/dev`: `4cde57bd1004a384d7b0c9f83f73ced209bdc742`
- `origin/main`: `4cde57bd1004a384d7b0c9f83f73ced209bdc742`
- remotes equal: true
