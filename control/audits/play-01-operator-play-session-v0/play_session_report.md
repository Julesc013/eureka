# Play Session Report

The PLAY-01 report schema is `play_session_report.v1`.

Required operator sections:

- instance
- seed_state
- queries
- search_results
- absence
- absence_results
- hunts
- search_needs
- workunits
- blocked_future_actions
- server_routes_if_checked
- server
- validation
- warnings
- boundaries
- next_actions

The report keeps compatibility fields from PLAY-00 where practical so existing
smoke checks can continue to read `known_hit_result`, `known_absence_result`,
and blocked WorkUnit IDs.
