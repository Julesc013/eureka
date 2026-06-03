# Compatibility And Degradation Spec

## Required Profiles

- `json_v0`
- `text_v0`
- `html_basic_v0`
- `snapshot_v0`

## Forward Compatibility

- unknown fields ignored
- unknown status displayed as `unknown`
- unknown actions hidden or marked unsupported
- unknown evidence types linked but not interpreted
- unsupported profile falls back to text, JSON, or safe HTML

## Accessibility

Every status has text, every action has a label, every icon has a text
equivalent, every graph has a list fallback, every filter has a form fallback,
and every reason can render as plain text.

