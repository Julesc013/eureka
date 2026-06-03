# Capability Negotiation Spec

## Safe Order

1. explicit query parameter
2. account/device preference if available and public-safe
3. native/relay capability manifest if available
4. host profile
5. HTTP Accept, language, and encoding
6. safe user-agent fallback
7. safest default: server-rendered no-JS HTML

## Compatibility Rules

- unknown fields ignored
- unknown status shown as `unknown`
- unknown action hidden or shown unsupported
- unknown evidence type linked but not interpreted
- unsupported renderer profile falls back safely

