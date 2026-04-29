# Remediation

If the drift guard fails:

1. Identify the failed artifact group in the plain or JSON report.
2. Run the owning check command directly.
3. Inspect the source inputs listed in `generated_artifacts.json`.
4. If the source change is intentional, run the owning update command for
   generated artifacts or perform a bounded governed edit for hybrid metadata.
5. Rerun the drift guard and the related validator lane.
6. Run `git diff --check` before committing.

Do not edit generated outputs by hand unless the owning generator is deliberately
not responsible for that file and the inventory is updated to say so.

Do not use this guard to deploy, fetch external data, run live probes, scrape,
crawl, or record external baselines.

