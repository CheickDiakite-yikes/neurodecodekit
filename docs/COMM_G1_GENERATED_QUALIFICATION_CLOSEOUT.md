# COMM-G1 Generated Qualification Closeout

**Date:** 2026-08-27  
**Execution status:** consumed; no rerun  
**Closeout route:** `COMM-G1-R0`  
**Scientific value:** none

## What executed

After implementation commit `5621fb8e378def319f6529e3d3173ffc88dbe9af`
passed Base Python job `98439231456`, Optional Neuro Readers job
`98439231761`, and CI `33048855198`, the one registered generated-only
qualification executed once.

The immutable public result is
`registries/comm_g1_generated_qualification_result.v0.json`: 6,271 bytes,
SHA-256 `696fe4236a5ff45b1b9a61761e6381f456a5e722aa5fa03fffa4008a3e29ce4e`.
The executor reported:

| Measure | Observed |
|---|---:|
| Runtime | 29.46742837491911 s |
| Peak process-tree RSS | 223,526,912 bytes |
| Generated input | 33,030,144 bytes |
| Maximum private generated prediction payload | 244,033 bytes |
| Public output | 6,271 bytes |
| Parameter updates | 60 |
| Model inference runs / prediction sets | 60 / 60 |
| Prediction rows | 1,440 |
| Synthetic target deliveries / scores | 1 / 1 |
| Post-target updates | 0 |
| Reported adversarial refusals | 35 |
| Executor route on injected fixture | `COMM-G1-R1` |

Every real/private-path, real-signal, real-target, real-model, network, provider,
stream, device, release, and claim counter was zero.

## Why the score is not accepted

Immediate artifact-only review found three prospective acceptance failures:

1. The replay fingerprint binds item, participant, session, trial, repeat,
   synthetic target, and signal bytes, but omits cue, timing, sample/time bounds,
   sampling rate, true length, padding mask, channel names, roles, and geometry.
   Identical hashes for `cue_only`, `timing_only`, and `no_signal` make this gap
   visible in the immutable result.
2. The two deterministic generations occurred in one process. These were not the two separate clean workdirs required by the contract.
3. The official 35-ID refusal ledger includes clobber and nonregular-output
   cases but does not explicitly exercise the registered `symlink_escape` and
   `resource_cap_breach` families.

These are generated proof-completeness defects, not evidence that the numerical
model is wrong. They nevertheless prevent acceptance under the preregistered
router. The executor's internal `COMM-G1-R1` value is therefore retained as raw
output but rejected at closeout. The binding closeout route is `COMM-G1-R0`:
structural/proof completeness failure with no accepted synthetic score.

## Boundaries

The invocation is consumed. It may not be rerun, repaired in place, overwritten,
or reinterpreted as accepted. The exact implementation and exact result remain
immutable evidence of what happened.

No real EEG was accessed. No communication decoding, EEG-beyond-peripheral
information, unseen-person generalization, independent replication, live
decoding, hardware performance, or clinical result is established.

## Next gate

A future generated qualification must use a new lane identifier and prospective
contract. It must bind every generated input field in its replay digest, create
two genuinely isolated workdirs, and exercise every named adversarial family
before a score can be accepted. It may reuse the frozen scientific model family
but may not rerun COMM-G1 or loosen its failure record. Every real-data operation
still requires a separate Tier C packet and decision.
