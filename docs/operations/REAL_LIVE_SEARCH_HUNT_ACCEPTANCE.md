# Real Live Search/Hunt Acceptance

This runbook is for the local operator. Do not paste provider keys into chat,
commits, logs, or evidence artifacts.

The normal canary path uses `--provider auto`. It selects any configured,
approved broad-web provider. Internet Archive metadata may supplement archive
queries, but IA alone does not satisfy the general broad-web canary.

1. Configure one broad-web provider key locally:

   ```powershell
   $env:BRAVE_SEARCH_API_KEY="<your-key>"
   # or
   $env:MOJEEK_SEARCH_API_KEY="<your-key>"
   ```

2. Bootstrap a local acceptance instance:

   ```powershell
   python scripts/eureka.py --instance ..\instances\live-acceptance bootstrap --no-demo
   ```

3. Run preflight. It reports readiness and never prints the key:

   ```powershell
   python scripts/eureka.py --instance ..\instances\live-acceptance canary preflight --provider auto --live-check --json
   ```

4. Run the real end-to-end canary with a genuinely unseen query:

   ```powershell
   python scripts/check_live_search_hunt_acceptance.py `
     --live-canary `
     --query "<a genuinely unseen query>" `
     --instance ..\instances\live-acceptance `
     --provider auto `
     --max-queries 3 `
     --max-fetches 3 `
     --keep-instance `
     --evidence-out ..\instances\live-acceptance\exports\canary-evidence.json `
     --json
   ```

5. Start the product:

   ```powershell
   python scripts/eureka.py --instance ..\instances\live-acceptance serve --live
   ```

6. Open the displayed local URL.

7. Enter an unseen query.

8. Use Hunt deeper.

9. Verify that at least one fetched and indexed result remains findable after
   restarting Eureka.

Inspect JSON only when troubleshooting. The product acceptance verdict remains
a separate human judgment.
