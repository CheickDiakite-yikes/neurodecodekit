# BNCI-C3C5-1 Stage G1 Generated Qualification Result

Date: 2026-08-24

Status: **the sole replacement generated/mock qualification passed; result
proof is pending and Stage A has not begun**

Machine result:

- `registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_result.v0.json`

## Proof Before Execution

Recovery decision commit `c5dd49b3d29fcb348fc836812f5a48a6c5526f04`
passed Base Python job `97547643345` in 6m36s, Optional Neuro Readers job
`97547643658` in 8m32s, and CI `32763519623`. Only after both jobs were green
did the one replacement qualification run.

The invocation used the frozen implementation, one CPU thread, one worker,
one numerical job, generated MAT fixtures, mocked transport, generated signal
and targets, and one invocation-owned temporary root. It used no network and
opened no real, existing, ignored, consumed, or other-project payload.

## Result

Route: `passed_generated_mocked_qualification_only`

All 11 registered engineering case classes passed, including:

- strict generated MAT structure and target-firewall checks;
- causal future-impulse and feature-dimension replay;
- nine outer and eight inner participant firewalls;
- exact E1/E2/control fit schedules;
- canonical prediction freezing and mutation refusal;
- target-swap and checkpoint invariance;
- transport integrity and resume behavior;
- overwrite, alias, output, disk, RSS, and second-publication refusals; and
- aggregate sign-flip and router scoring.

The generated router emitted `BNCIC3C5-R2`. That synthetic route has no
scientific or claim value.

## Measurements

| Measure | Observed | Cap |
|---|---:|---:|
| Generated input | 56,033,424 bytes | 536,870,912 private bytes |
| Aggregate output | 3,296 bytes | 4,194,304 bytes |
| Runtime | 17.790334874996915 s | 3,600 s |
| Peak process-tree RSS | 566,231,040 bytes | 1,073,741,824 bytes |
| Initial free disk | 98,884,259,840 bytes | at least 5,368,709,120 bytes |
| Outer isolated folds | 9 | exactly 9 |
| Synthetic fits | 468 | exactly 468 |
| Synthetic prediction sets | 495 | exactly 495 |
| Prediction rows | 3,456 | bounded generated rows |
| Synthetic target deliveries | 1 | exactly 1 |
| Synthetic scoring events | 1 | exactly 1 |

Additional measurements:

- generated MAT runs / trials: 6 / 288;
- generated feature / held-target rows: 432 / 216;
- held-out target capabilities inside fold workers: 0;
- network / new payload bytes: 0 / 0;
- raw-data / real-cache reads: 0 / 0;
- real MAT, signal, event, artifact, target, or label reads: 0;
- real fits / inference runs / prediction sets: 0 / 0 / 0;
- real target deliveries / scoring events: 0 / 0;
- retained generated payload bytes: 0;
- producer causal: yes; and
- end-to-end latency measured: no.

The canonical 3,296-byte source output has SHA-256
`b63ac687fcd6fad38868a7c2081ef1a50c3a3f1be3cbf3e0cfb78632d22d50c6`.
It is represented by the aggregate machine result and is not committed as
temporary execution debris.

## One-Shot Boundary

The replacement qualification invocation count is one and it is consumed.
It may not be retried, rerun, resumed, restarted, or scored again. Only the
3,296-byte aggregate source output remained after invocation-owned generated
payload cleanup.

## Local Closeout Verification

- result tests: 8 passed in 0.102 seconds;
- focused BNCI tests: 72 passed in 5.474 seconds;
- complete dependency-free suite: 5,992 passed with 216 expected skips in
  209.134 seconds;
- pinned Ruff, Python compilation, all JSON registry parsing, and
  `git diff --check`: passed.

These checks did not repeat the qualification, open a real payload, deliver a
real target, or run another score.

This exact result must be tested, committed, pushed, and pass both remote CI
jobs before Stage A. This closeout performs no Stage A, acquisition, real MAT,
model, target, score, release, or claim operation.

Engineering capability added: the complete target-firewalled BNCI pipeline
now passes its bounded generated/mock end-to-end qualification across all nine
isolated participant folds and every registered control class.

Scientific claim not established: no real BNCI neural payload was opened or
scored, so this result establishes no decoding accuracy, unseen-person
generalization, EEG-beyond-EOG advantage, movement-intention or motor-cortex
origin, language or thought decoding, live use, or portable-hardware result.
