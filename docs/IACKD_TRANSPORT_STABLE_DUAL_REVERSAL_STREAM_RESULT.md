# IACKD-2R Transport-Stable Stream Result

Date: 2026-08-11

Status: **Consumed and parked at `IACKD2R-F05`; no retry or rerun**

Machine result:
`registries/iackd_transport_stable_dual_reversal_stream_failure_result.v0.json`

## Ordered Proof Before Execution

Packet-bound decision `feef8f7` passed CI `31476158747`. Exact additive
implementation `b32dc25e94efc15bcb4288db9bb5a4c0d4172ed5` then passed Base
Python job `93736708777` and Optional Neuro Readers job `93736708868` in CI
`31478167292`.

Only after both jobs were green did the sole registered invocation begin under
one CPU thread, one worker, and one numerical job.

## What Happened

The pre-consumption machine gate passed. The executor then wrote the new
268-byte no-retry marker at `2026-08-11T09:35:45.049689Z` and opened the first
registered dataset-description response.

The response passed:

- HTTP status and exact final URL;
- redirect refusal;
- framing and identity-content-encoding checks; and
- the exact registered observed body count of 1,178 bytes.

The executor performed one SHA-256 computation. The observed digest did not
match the pinned committed digest
`275cf1d24f93832ed17fd32d46a589286453042f8d2788b4f3dc1933c6523d93`.
It failed closed at nested refusal `IACKDT-F07` and public route
`IACKD2R-F05` before semantic parsing.

The observed digest, framing profile, `Content-Length` state, changed fields,
exact machine measurements, pipeline RSS, and pipeline runtime were not
retained. The raw body was not persisted. The command's externally observed
wall time was 0.917392875 seconds.

## Exact Counters

```text
registered invocations:          1
machine-safety checks:           1 passed
metadata response opens:         1
metadata body reads / bytes:     1 / 1,178
metadata hashes / matches:       1 / 0
metadata semantic parses:        0
selected payload requests/bytes: 0 / 0
EEG/header/channel/event reads:  0
signal/trajectory/target reads:  0
derivative writes:               0
fits / inference / predictions:  0 / 0 / 0
freezes / target deliveries:     0 / 0
scores / post-target updates:    0 / 0
retries / reruns:                0 / 0
old-root or retained-bundle ops: 0
private generated file bytes:    268
public result bytes before closeout: 0
```

The new private root contains only the consumed marker. No raw or derivative
file exists.

Closeout verification passed 34 focused tests, the complete 2,035-test base
suite with 204 skips, and the complete 2,091-test optional-neuro suite with 34
skips. Ruff 0.15.20, compileall, all 150 registry JSON files, and
`git diff --check` also passed.

## Interpretation

The transport repair worked as designed: an absent or advisory
`Content-Length` no longer blocks a standards-valid response, but a body hash
remains authoritative. The live public metadata body now differs from the
pinned body while retaining the same byte count. Because parsing was blocked,
this run does not say whether the difference is benign formatting, metadata
maintenance, or a substantive dataset change.

That distinction cannot be investigated by retrying this consumed lane. A
future attempt would require a separately named prospective metadata-version
reverification contract with fresh immutable identity and Tier C permission.
It must not silently amend or reopen IACKD-2R.

## Stop Boundary

IACKD-2R is consumed. Do not request the URL again, compute another body hash,
inspect changed fields, reuse or alter the marker, resume the stream, create a
derivative, run analysis, freeze predictions, open targets, or score under this
contract.

Engineering result: the transport-stable additive executor correctly rejected
real public metadata content drift after one bounded read and before semantic
or EEG access.

Scientific claim not established: no EEG payload, signal, event, trajectory,
target, derivative, model, prediction, freeze, or score was reached, so this
result establishes no neural effect, action decoding, brain-specific origin,
unseen-person generalization, language or thought decoding, real-time
operation, portable hardware, home use, assistive benefit, or clinical utility.
