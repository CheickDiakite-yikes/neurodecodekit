# MARC2-VR14P Generated Qualification Result

Date: 2026-08-20

Route: `MARC2VR14P-G1`

Disposition: passed and consumed generated qualification; real aggregate read
remains closed

## Result

All eight frozen aggregate routes appeared exactly four times across canonical
and reversed order with two exact replays. All 32 paths matched, and the replay
digest was
`94d920bfcf235f3950311ea64553e9742a744038e9f6104dbbf8dc8ab357bcc6`.

The fixed-path generated state machine validated one 1,526-byte canonical
source report and one 1,925-byte recovery receipt under a temporary root. The
root was removed and retained output was zero.

The qualification passed 89 direct refusals spanning decision drift, malformed
or noncanonical JSON, route and schema mutations, resource drift, leakage
keys, symlinks, path traversal, output collision, and the 65,536-byte input
cap.

## Measurements

```text
generated input bytes:       50,370
aggregate output bytes:      2,058
retained output bytes:       0
runtime seconds:             0.008616000006441027
peak RSS bytes:              28,901,376
CPU / workers / jobs:        1 / 1 / 1
network / new payload:       0 / 0 bytes
```

Every real aggregate-report, recovery-output, readiness, consumed-marker,
structural-source, private-manifest, archive, neural, target, model,
prediction, score, FW2/CIL1, other-project, retry, and claim counter was zero.

Engineering capability proven: the generated interface can strictly recover
one allowlisted aggregate route while refusing malformed or leaking inputs.

Scientific claim not established: no real or ignored output, neural payload,
target, model, prediction, or score was accessed, so this result establishes no
neural effect or decoding performance.
