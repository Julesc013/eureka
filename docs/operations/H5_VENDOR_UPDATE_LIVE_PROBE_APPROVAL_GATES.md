# H5 Vendor/Update Live Probe Approval Gates

Every source starts `not_approved_for_live_access`. Before any external call, committed policy must approve live access, metadata probe scope, exact source ID, exact request key, endpoint or metadata class, timeout, retry budget, request budget, cache or no-cache posture, kill switch, auth/no-auth posture, and output paths.

The same policy must keep source sync, catalog sync, public-query fanout, downloads, vendor tools, package managers, firmware flashing, install, execution, scraping, and crawling disabled.
