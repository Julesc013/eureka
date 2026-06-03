# Degradation Model

Degradation is a feature. Eureka should return the best honest state rather
than pretend uncertainty is truth.

## Search Degradation

```text
reviewed local result
-> reviewed near match
-> candidate from reviewed source observation
-> candidate from fallback observation
-> known need
-> known absence
-> policy_blocked
-> unavailable
```

## Representation Degradation

```text
rich HTML
-> basic HTML
-> classic/old-browser HTML
-> text
-> JSON manifest
-> static snapshot
```

## Action Degradation

```text
direct safe action
-> manifest
-> citation
-> source observation
-> blocked reason
-> unavailable reason
```

## Source Degradation

```text
reviewed local index
-> cached source observation
-> bounded metadata lookup
-> source unavailable state
-> SearchNeed
```

