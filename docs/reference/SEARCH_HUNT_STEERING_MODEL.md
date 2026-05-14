# Search Hunt Steering Model

Steering preferences are local operator constraints or preferences for future Search Hunt work. They are stored in `search_hunt_steering_preferences` and linked to command history.

Supported steering types:

- `include_source_family`
- `exclude_source_family`
- `prefer_official_sources`
- `allow_community_sources`
- `metadata_only`
- `allow_extraction_future`
- `disallow_extraction`
- `allow_ai_escalation_future`
- `disallow_ai_escalation`
- `add_note`
- `set_priority`

Each preference records a command id, hunt id, type, value, reason, operator label, active flag, limitations, warnings, and timestamps.

Preferences can guide future HUNT-06 WorkUnit creation, but they do not create work in HUNT-03.
