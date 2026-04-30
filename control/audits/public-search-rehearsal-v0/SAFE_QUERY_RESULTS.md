# Safe Query Results

The local rehearsal ran representative safe queries through
`/api/v1/search`. A zero-result response is valid when the response remains a
governed success envelope with absence/gap information.

| Query | Status | Result count | Envelope ok | Cards aligned | Warnings | Limitations or absence | Private path leakage |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| `windows 7 apps` | pass | 10 | yes | yes | yes | yes | no |
| `latest firefox before xp support ended` | pass | 0 | yes | yes | yes | yes | no |
| `driver.inf` | pass | 10 | yes | yes | yes | yes | no |
| `thinkpad t42 wifi windows 2000` | pass | 10 | yes | yes | yes | yes | no |
| `registry repair` | pass | 10 | yes | yes | yes | yes | no |
| `blue ftp` | pass | 10 | yes | yes | yes | yes | no |
| `pc magazine ray tracing` | pass | 9 | yes | yes | yes | yes | no |
| `archive` | pass | 10 | yes | yes | yes | yes | no |
| `no-such-local-index-hit` | pass | 0 | yes | yes | yes | yes | no |

The rehearsal does not claim broad search usefulness or completeness. The
queries prove that the local/prototype runtime can produce governed result or
absence envelopes under bounded inputs.
