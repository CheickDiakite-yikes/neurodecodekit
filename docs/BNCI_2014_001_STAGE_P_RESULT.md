# BNCI-C3C5-1 Stage P Prediction-Freeze Result

Date: 2026-08-25

Status: **Passed once and consumed. The exact target-blind prediction freeze is
pending commit, push, and both required CI jobs. Stage T remains closed.**

## Result

The sole remotely activated Stage P invocation completed all nine
participant-held-out folds over the existing private Stage Q derivatives.
It produced:

- 468 parameter-update fits;
- 495 model-inference runs and prediction sets;
- 41,472 private prediction rows across 16 frozen conditions;
- 11,288,910 private prediction bytes and 11,298,505 total private output
  bytes;
- one 5,037-byte aggregate public freeze with SHA-256
  `468fd77f45645620ff2636a3b00f587986d1ce0f73c4cad88896a8bd9b354057`;
- 55.674016 seconds runtime; and
- 629,194,752-byte peak process-tree RSS.

Free disk moved from 93,582,200,832 to 93,571,207,168 bytes. No network byte,
held-out-E target, held-out-T signal or target, score, post-target update, or
rerun occurred.

## Firewall Evidence

The executor accepted the exact nine-fold inventory and the exact 6-run x
48-trial held-out-E grid for every person. Every held-out person had zero
calibration. All private predictions were canonicalized and hashed before any
target delivery. The public artifact contains aggregate commitments and counts,
not an individual prediction, probability, target, participant outcome, model
coefficient, private path, or scoring key.

The private predictions are committed by SHA-256
`b5480077335c0b614e8423673a0f7c3dbfe994796d737529c98ae3c18e66d12d`.
The Stage Q source capability is bound by a private-key HMAC, and the nine
encrypted target envelopes plus scoring-key vault are bound by a separate
aggregate transport commitment. Stage T must verify all three bindings.

## Source-Only Selection

The frozen source-only selector chose E1 in all nine folds and E2 in zero.
This says that the preregistered E1 candidate won the already-frozen
source-participant selection rule consistently. It does not say that E1 is
accurate on the held-out people, beats no-signal or timing controls, or adds EEG
information beyond EOG. Those questions remain unobserved until Stage T.

## Runtime Warning

Scikit-learn emitted repeated `ConvergenceWarning` messages because some frozen
LBFGS fits reached the preregistered 80-iteration limit. Console output was not
retained, so an exact warning count is unavailable. The warning class and cause
are recorded here; no iteration, scaling, solver, model, threshold, seed, or
selection rule was changed, and the consumed run was not repeated.

## Next Barrier

Commit and push the exact prediction freeze and this aggregate closeout, then
require Base Python and Optional Neuro Readers to pass remotely. Only after
that proof may a separate Stage T activation be created and remotely green.
Stage T may deliver the same nine sealed held-out-E target sets and score once;
it may not train, tune, exclude, recalibrate, retry, or rerun.

## Claim Boundary

Engineering capability established: the real target-firewalled BNCI
derivatives were converted into complete, hash-frozen, held-out-participant
predictions under the registered resource and operation limits.

Scientific claim not established: targets remain sealed and no score exists,
so Stage P alone does not establish unseen-person prediction, EEG advantage
beyond recorded EOG, decoding performance, thought or language decoding,
movement intention, motor-cortex origin, live decoding, portable hardware, or
clinical utility.
