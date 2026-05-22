# Live Source Action Policy

Live source actions are policy-gated commands executed through the headless run
kernel command path. A surface may request a command, but policy decides whether
the command can proceed.

For this foundation, the only live-capable source action is the Internet Archive
metadata lane. It is not enabled by default and is not public search fanout.

Required gates:

- Operator projection.
- Explicit command.
- Operator token for live execution.
- Request caps for rows, HTTP requests, and timeout.
- Redacted summaries and normalized previews only.
- Candidate-only output.

Forbidden behavior:

- Raw response persistence.
- Downloads or file fetches.
- Extraction, execution, installation, or emulation.
- Model/provider calls.
- Operator instance or index mutation.
- Production or public launch readiness claims.
