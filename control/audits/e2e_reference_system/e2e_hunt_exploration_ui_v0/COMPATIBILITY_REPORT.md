# Compatibility Report

Existing local Workbench routes are preserved.

The old `/runs` route remains process-local. The new `/explore/runs` route reads durable E2E Reference Runner bundles, satisfying the persistence requirement without changing `/runs` compatibility.

Existing public-alpha read-only route posture is unchanged.

