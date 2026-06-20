# Real Live Search/Hunt Acceptance

This runbook is for the local operator. Do not paste provider keys into chat,
commits, logs, or evidence artifacts.

1. Configure the Brave key locally:

   ```powershell
   $env:BRAVE_SEARCH_API_KEY="<your-key>"
   ```

2. Bootstrap a local acceptance instance:

   ```powershell
   python scripts/eureka.py --instance ..\instances\live-acceptance bootstrap
   ```

3. Run the real end-to-end canary with a genuinely unseen query:

   ```powershell
   python scripts/check_live_search_hunt_acceptance.py `
     --live-canary `
     --query "<a genuinely unseen query>" `
     --instance ..\instances\live-acceptance `
     --max-queries 3 `
     --max-fetches 3 `
     --keep-instance `
     --json
   ```

4. Start the product:

   ```powershell
   python scripts/eureka.py --instance ..\instances\live-acceptance serve --live
   ```

5. Open the displayed local URL.

6. Enter an unseen query.

7. Use Hunt deeper.

8. Verify that at least one fetched and indexed result remains findable after
   restarting Eureka.

Inspect JSON only when troubleshooting. The product acceptance verdict remains
a separate human judgment.
