# MARC1-P1A Live Metadata Selection Result

Date: 2026-08-12

Status: **Consumed at `MARC1PS-F03`; no retry or rerun is available**

Machine result:
`registries/marc1_privacy_preserving_pilot_selection_live_result.v0.json`

## Result In One Line

The one target-free metadata selection failed closed because the terminal
Wrist response did not satisfy the frozen explicit identity-encoding rule.
No public response body, archive payload, EEG sample, target, model, or score
was read or produced.

## Proof Order

Exact selector commit
`702e61377d41fd1d95939d5e4047be59e4631d4d` passed Base Python job
`94056321843` and Optional Neuro Readers job `94056321914` in CI
`31578614616` before the one invocation. Its implementation registry SHA-256
was `054ae02821b715de99b1b1ffe1eb2d3efb3a31c690fa4e18b2f31dae31a8c9ab`.

The pre-consumption machine gate passed before the private marker or either
real input:

```text
free disk:                         16,802,996,224 bytes
logical CPUs:                     12
one-minute load:                  7.23486328125
load per logical CPU:             0.6029052734375
pre-consumption peak RSS:         32,342,016 bytes
CPU threads / workers / jobs:     1 / 1 / 1
```

The private consumed marker was then written. This execution is final even
though selection did not complete.

## Observed Failure

The executor performed the registered no-follow validation and exactly one
content open, bounded read, SHA-256 pass, and strict parse of the 418,755-byte
Freewill inventory. It then opened one response to the frozen Wrist metadata
request and refused at `MARC1PS-F03` because the terminal response did not
meet the contract's explicit identity `Content-Encoding` condition.

The executor did not retain or publish the observed header value. It did not
read or hash the public response body, parse a Wrist row, select a participant,
or create the private 300-row selection manifest. The access counter records
one request and one response open; the transport summary remains zero because
no terminal response body was accepted.

This is a transport-contract result, not evidence against the preregistered
cohort or against a neural hypothesis.

## Access And Resource Result

```text
Freewill path operations / opens:       1 / 1
Freewill reads / hashes / parses:       1 / 1 / 1
Freewill input bytes:                   418,755
Wrist requests / response opens:        1 / 1
Wrist body reads / body bytes:          0 / 0
selected participants / private rows:   0 / 0
archive payload requests / bytes:       0 / 0
signal / target reads:                  0 / 0
training / inference / scoring:         0 / 0 / 0
internal runtime:                       0.5323725419584662 sec
reported peak RSS:                      37,289,984 bytes
external wall time:                     0.74 sec
external maximum RSS:                   37,371,904 bytes
public result bytes:                    4,706
incremental disk bytes:                 5,159
```

Public result SHA-256:
`3c526ac52f8185f3fe29b8f3843fd808cd9646b5011e9638d6bf55f5a459153a`

Every payload, signal, event, target, derivative, training, inference,
prediction, freeze, delivery, score, provider-model, hardware, release,
post-result update, rerun, and claim-upgrade counter remained zero.

## Verification

Ten immutable result tests and all 339 MARC tests pass. The complete
dependency-light suite passes 2,478 tests with 204 expected skips in 20.462
seconds at 267,026,432-byte external peak RSS. The optional-neuro suite passes
2,549 tests with 35 expected skips in 56.866 seconds at 731,791,360-byte
external peak RSS. Both complete suites add exactly ten tests and zero skips
over the green selector baseline.

Ruff, compileall, strict parsing of every registry JSON document, aggregate
result inspection, and `git diff --check` also pass.

## Disposition

`MARC1-P1A` is consumed and cannot be retried, rerun, resumed, or amended.
The retained Freewill inventory and private consumed marker must not be opened
again under this lane. No payload-acquisition packet is eligible because the
joint pilot selection did not complete.

The next prospective step is a separately named metadata transport-semantics
recovery. It must freeze, on generated and mocked responses, whether an absent
`Content-Encoding` and an explicit `identity` value are equivalent unencoded
representations while continuing to reject every actual content coding,
duplicate critical header, automatic redirect, private destination, oversized
body, alternate endpoint, retry, and fallback. A new Tier C decision would be
required before another real metadata request or private-inventory read.

This remains a confound-resolution rung on the same thought-to-text research
path, not a pivot. A transport repair cannot itself establish neural or
language evidence.

## Claim Boundary

Engineering capability added: NeuroDecodeKit consumed one proof-gated metadata
attempt and failed closed with an aggregate, privacy-preserving audit record
before accepting any public body or opening any neural payload.

Scientific claim not established: this transport failure establishes no neural
effect, decoding accuracy, language decoding, or thought-to-text capability.
