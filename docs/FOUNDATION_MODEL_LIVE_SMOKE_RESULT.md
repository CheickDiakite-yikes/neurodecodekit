# FM-1 Synthetic Terra Provider Result

**Date:** 2026-08-08
**Status:** Consumed and parked after one partial invocation; no rerun
**Model:** `gpt-5.6-terra`
**Evidence:** The committed 7,327-byte synthetic fixture only

## Result

FM-1 did not pass its full provider qualification. The one authorized
invocation attempted three sequential Responses API calls. Two returned
completed, schema-valid structured outputs. The third, the first matched
synthetic-evidence request, returned a provider response whose status was not
`completed`. The runner wrote a sanitized terminal receipt and stopped without
retrying, exactly as the one-shot failure rule required.

The planned 12-call matrix therefore remains incomplete:

| Request | Condition | Outcome | Structured behavior |
|---:|---|---|---|
| 0 | `FM-A00`, language-only | completed and schema-valid | abstained, empty text, `evidence_used=none` |
| 1 | `FM-A01`, CTC-only | completed and schema-valid | returned `HELLO WURLD`, `evidence_used=ctc` |
| 2 | `FM-A02`, matched CTC plus synthetic key evidence | terminal failure | provider status was not completed; body retained only as byte count and SHA-256 |
| 3-11 | remaining matrix | not attempted | unavailable after the no-retry stop |

There is no complete `FM-A01` versus `FM-A02` pair and no completed `FM-A03`
derangement condition. Evidence-sensitivity comparison is therefore
unavailable. The two completed responses demonstrate transport and strict
parsing for those requests only.

## Measurements

```text
invocations:                               1
API credential reads:                      1
provider/network calls attempted:          3
completed responses:                       2
schema-valid responses:                    2
refusals:                                  0
retries:                                   0
input tokens, completed responses:       339
cached input tokens:                       0
cache-write input tokens:                  0
output tokens, completed responses:      143
reasoning tokens:                         62
estimated cost, completed responses:  $0.002394
wire request bytes:                    4,179
wire response bytes:                  13,502
runtime:                            8.406004 s
peak RSS:                         39,337,984 bytes
sanitized result bytes:                5,882
```

The estimated cost is computed from usage attached to the two completed
responses. Usage for the non-completed third response was not admitted into the
strict result schema, so the local estimate is not a complete bill for all
three attempts. Provider accounting is authoritative and the third attempt's
actual charge is unavailable locally.

Completed-response latencies were 2.386448417 seconds for `FM-A00` and
2.260840833 seconds for `FM-A01`. The total runtime includes the third attempt
and receipt construction. End-to-end neural capture latency was not measured.

The ignored sanitized result is 5,882 bytes with SHA-256:

```text
f1ff632c45bc0a6c60fcec865615bf7becf07589f5d3a3472f26492c2ee5756e
```

The terminal response contributed 5,720 wire bytes and is bound by SHA-256:

```text
c13d1e7c5ff6dd9440564c63b7f69e6ad877b89b00e0dcfe91b7043eb4b503cf
```

Neither response body, provider response ID, header, organization metadata,
nor credential is committed.

## Gate Outcome

| Gate | Outcome |
|---|---|
| Contract, decision, fixture, plan, and request hashes | pass |
| Exact implementation commit pushed and remotely green | pass, `a1d7ccca514223cfc49bd37ef80c58c9cbc4596f`, CI `31269398670` |
| One credential read | pass |
| Fixed Terra endpoint/model/settings | pass for attempted calls |
| Exactly 12 completed sequential requests | fail, 3 attempted and 2 completed |
| Strict structured output for every completed response | pass, 2/2 |
| All four conditions available for all three items | fail |
| No retry or substitution | pass |
| Runtime, RSS, output, call, token, and estimated-cost caps | pass for retained measurements |
| No protected content, target, raw/dense neural upload, training, fine-tuning, or scoring | pass |
| Behavioral matched-versus-deranged comparison | unavailable |
| Scientific or decoding claim | unavailable |

## Failure Boundary

The registered terminal category is `provider_response_not_completed` at
request index 2. This proves only that the provider returned a non-completed
status for that request. Because the sanitized receipt deliberately excludes
the raw body and incomplete-detail fields, it does not establish whether the
cause was output budget, provider capacity, policy, or another service-side
condition. Calling one of those a root cause would exceed the evidence.

FM-1 is consumed. Do not rerun it, increase the output budget, substitute Sol
or Luna, retry only the missing condition, or tune prompts from these outputs
under this contract. A future provider qualification would require a new
hypothesis, contract, exact decision, and independent fixture.

## Access Accounting

```text
real or protected data reads:       0
target or reference reads:          0
raw or dense neural uploads:        0
training runs:                      0
fine-tuning runs:                   0
scoring runs:                       0
```

Engineering capability added: NeuroDecodeKit demonstrated bounded live Terra
transport and strict parsing for two synthetic requests, plus honest
fail-closed parking and receipt construction on the third.

Scientific claim not established: no real neural evidence or target was used,
the four-arm matrix did not complete, and FM-1 establishes no decoding
accuracy, neural advantage, brain-specific information, generalization,
real-time operation, portable hardware, home use, or clinical utility.
