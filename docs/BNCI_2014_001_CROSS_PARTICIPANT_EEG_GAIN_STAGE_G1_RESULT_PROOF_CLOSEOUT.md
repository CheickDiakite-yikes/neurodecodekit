# BNCI-C3C5-1 Stage G1 Result Proof Closeout

Date: 2026-08-24

Status: **proof-only closeout recorded; effective after this exact closeout is
committed, pushed, and both required CI jobs are green**

Machine proof:

- `registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_result_proof.v0.json`

## Remotely Green Result

Exact result commit `4ef12dd056358907ab6734c7a2a21e6776f6f6af` passed:

- Base Python job `97553936562` in 5m30s;
- Optional Neuro Readers job `97553936838` in 6m51s; and
- CI `32765504463`.

The closeout binds the unchanged result document, machine result, and result
test: three artifacts totaling 17,134 bytes under canonical artifact-set
SHA-256:

```text
90f006d84089af6167ad920d5c90a0ea434cf28b0c04a60ef883ef373649f58b
```

## What Is Closed

The sole replacement generated/mock G1 invocation passed all 11 registered
case classes across nine isolated folds. Its exact schedule was 468 synthetic
fits, 495 synthetic prediction sets, one generated target delivery, and one
synthetic score. It ran in 17.790334874996915 seconds at 566,231,040-byte peak
process-tree RSS, emitted 3,296 aggregate bytes, and retained zero generated
payload bytes.

The invocation is consumed. This proof does not repeat, resume, restart, or
re-score it. The synthetic `BNCIC3C5-R2` route remains scientifically inert.

## Proof-Only Operations

This closeout performs one GitHub CI status verification and local reads of
the three committed aggregate artifacts. It performs zero qualification,
generated MAT, mocked transport, fit, prediction, target delivery, scoring,
network, payload, real-data, Stage A, release, or claim operations.

Local verification passed six proof tests, all 78 focused BNCI tests in 5.651
seconds, and all 5,998 dependency-free tests with 216 expected skips in
209.524 seconds. Pinned Ruff, Python compilation, JSON registry parsing, and
diff hygiene also pass.

## Next Boundary

Commit, push, and green this exact proof-only closeout. After that proof, G1
is remotely closed and Stage A is the next ordered milestone under the
original packet-bound decision. This closeout itself stops before Stage A and
does not acquire, open, parse, or interpret a BNCI payload.

Engineering capability added: the generated target-firewalled BNCI pipeline
and its exact one-shot result now have a remotely proven, hash-bound closeout.

Scientific claim not established: generated fixtures are not neural evidence,
so no decoding, unseen-person, EEG-beyond-EOG, motor-cortex, thought,
language, live, portable, or clinical claim was established.
