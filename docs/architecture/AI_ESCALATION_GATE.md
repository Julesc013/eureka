# AI Escalation Gate

The AI escalation gate records whether a local Search Hunt has enough context for a future bounded research escalation. It is disabled by default and does not call any provider.

The gate consumes local context only: the Search Hunt Session, exhaustion report, SearchNeed, steering preferences, checked and deferred layers, policy-blocked actions, candidate context, absence context, and a disabled agent research task. A raw query alone is not enough input.

The runtime package is `runtime/ai_escalation`. It stores local gate records and preflight records in `db/ai_escalation.sqlite` through the local appliance manifest. Records carry `provider_enabled: false` and `execution_enabled: false`.

Future output classes are candidate material only: alias hypotheses, source leads, dead URL trace plans, archived URL trace plans, compatibility clues, provenance questions, extraction targets, candidate WorkUnits, and absence explanation drafts. Review remains required before anything can affect local state.

No source probes, extraction, browser automation, model/provider calls, review changes, public index changes, master index changes, site output writes, or deployment are enabled by this gate.
