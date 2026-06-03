# Renderer Policy

Renderers are pure projection functions:

```text
canonical view model + representation profile + skin + policy context
-> representation
```

They may simplify presentation, layout, media, and interaction. They must not
simplify away product meaning.

## Required Meaning

Every renderer must preserve:

- route identity
- object/result/source/need/candidate identity
- status
- evidence posture
- source posture
- risk and rights posture
- limitations
- allowed and blocked action posture
- canonical links or stable IDs

## Forbidden Behavior

Renderers must not:

- call source adapters
- fetch files
- run OCR or extraction
- mutate product truth
- make policy decisions
- hide candidate or verified status
- expose forbidden actions
- claim downloads, malware safety, rights clearance, installability, or artifact
  verification

## Placement

Renderer implementations belong under the future `runtime/surface/renderers/`
root. Skins belong under `site/assets/skins/` or examples/snapshot roots when
they are authored payloads. Product-facing surface packages remain under
`surfaces/`.
