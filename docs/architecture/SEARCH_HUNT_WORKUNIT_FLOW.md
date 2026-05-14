# Search Hunt WorkUnit Flow

Future hunts create WorkUnits through the WorkUnit queue. A WorkUnit records policy state, transition history, limitations, and typed outputs. WorkUnits do not equal truth. SourceProbe WorkUnits remain disabled until a future source-probe gate.

HUNT-01 does not create WorkUnits. It records unchecked/deferred layers so later HUNT tasks can explain what was not run.
