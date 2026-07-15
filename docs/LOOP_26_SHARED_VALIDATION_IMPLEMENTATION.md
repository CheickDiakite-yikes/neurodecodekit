# Loop 26/31/33 Shared S21 Validation Implementation

Date: 2026-07-15

Status: **Implementation complete and synthetically qualified; protected access
must wait for this exact commit to be pushed and remotely green**

Frozen design: `docs/LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md`

Machine contract: `registries/loop26_shared_validation_contract.v0.json`

Authorization decision: `registries/loop26_authorization_decision.v0.json`

## Purpose

This milestone implements the registered shared Loop 26/31/33 execution as five
separate, fail-closed stages. It does not execute those stages against the real
S21 cache. The separation exists so that implementation and synthetic isolation
tests can become remotely green before any protected cache value is accessed.

```text
static identities and headers
  -> one cache hash plus isolated derivatives
  -> 21 fits, 24 target-blind inferences, 6 priors, 31 prediction sets
  -> committed and remotely green hash-only freeze
  -> one six-target scoring delivery, then permanent consumed marker
```

## Added Interfaces

`src/neurodecodekit/cache/row_streaming_npz.py` provides bounded sequential
access to numeric NPY members inside a deflated NPZ archive. It rejects object
arrays, Fortran-order arrays, malformed headers, duplicate or invalid row
requests, scalar row streaming, and rows above the configured byte ceiling.
Its ledger distinguishes rows returned to the caller from excluded rows that
the deflate stream had to traverse opaquely.

`src/neurodecodekit/models/tiny_causal_sentence_ctc.py` implements the exact
2,908-parameter causal candidate and 2,884-parameter linear comparator. Every
fit uses deterministic CPU execution, one thread, fixed seeds, exactly 240 Adam
steps, no early stopping, no restart, no checkpoint selection, no gradient
clipping, and the registered CTC loss and greedy decoder. Checkpoints are
numeric NPZ payloads loaded with `allow_pickle=False`.

`src/neurodecodekit/evaluation/shared_s21_validation.py` implements the frozen
prefix order, six matched train-only priors, all registered attribution
transforms, private prediction payloads, hash-only prediction freeze records,
strict payload replay validation, all 64 sign assignments, and the registered
intersection-union and scaling decisions.

`src/neurodecodekit/experiments/shared_s21_validation_gate.py` enforces the
stage order, split binding, source and derivative identities, exact access
counters, parameter inventory, output caps, working-array bound, peak RSS,
thread limits, and one-shot target firewall. It never imports or calls the
legacy full-array sentence-cache loader.

## CLI

The five commands are deliberately staged:

```bash
neurodecode loop26-static-gate --help
neurodecode loop26-create-derivatives --help
neurodecode loop26-target-blind-gate --help
neurodecode loop26-inspect-freeze --help
neurodecode loop26-score --help
```

The registered execution order is:

```bash
neurodecode loop26-static-gate \
  --implementation-commit <remotely-green-implementation-sha>

neurodecode loop26-create-derivatives

neurodecode loop26-target-blind-gate \
  --implementation-commit <same-remotely-green-implementation-sha> \
  --freeze-record registries/loop26_prediction_freeze.v0.json

neurodecode loop26-inspect-freeze \
  --freeze-record registries/loop26_prediction_freeze.v0.json

# Commit and push only the hash-only freeze record and its invariant evidence.
# Wait for that exact commit to become remotely green before scoring.

neurodecode loop26-score \
  --freeze-record registries/loop26_prediction_freeze.v0.json \
  --green-freeze-commit <remotely-green-freeze-sha> \
  --public-report registries/loop26_shared_validation_result.v0.json
```

All derivative, checkpoint, plaintext prediction, validation-target, and
consumed-marker files stay under ignored `.codex_work/loop26/`. The committed
freeze contains hashes and measurements, never prediction text. The eventual
committed result contains numeric metrics and hashes, never target or
prediction text.

## Fail-Closed Boundaries

- The implementation commit must equal `HEAD`, the tracked worktree must be
  clean, and the frozen environment and one-thread settings must match before
  the static stage can pass.
- The real source cache receives exactly one full-file hash pass.
- The derivative stage returns exactly 55 train signal/target rows and six
  validation signal rows. It returns no validation targets and no source-test
  rows.
- The target-blind stage requires exactly 21 fits, 5,040 optimizer steps, 24
  model inferences, six priors, 21 checkpoints, and 31 prediction sets.
- Candidate and linear parameter counts must remain exactly 2,908 and 2,884.
- The scorer refuses a freeze file that is not tracked at the current green
  `HEAD`, or if any private prediction file, item order, length vector,
  configuration, checkpoint identity, transform, or prediction payload differs
  from its freeze row.
- The scorer creates its consumed marker before opening validation targets. An
  interruption or failure after that point parks the event; it cannot be
  restarted or rerun.
- Source-test rows, session 2, raw FIF/MAT, S7/S20/S25, network, downloads,
  language models, NeuroTokens, RW3, streams, devices, and hardware remain
  closed.

## Resource Contract

```text
CPU threads / workers:                1 / 1
candidate / linear parameters:        2,908 / 2,884
working arrays:                       <= 128 MiB
checkpoints:                          <= 4 MiB total
private prediction payloads:          <= 2 MiB total
all generated experiment artifacts:  <= 32 MiB
parameter-update runtime:             <= 1,200 sec
end-to-end runtime:                   <= 1,500 sec
peak RSS:                             <= 1 GiB
downloads:                            0 bytes
```

## Synthetic Qualification

The focused synthetic tests cover deterministic replay, causal future
invariance, exact parameter counts, fixed-step training, numeric checkpoint
roundtrips, malformed archives, forbidden object arrays, bounded row reads,
opaque traversal accounting, strict split binding, validation-target leakage,
deterministic controls, exact 31-set inventory, no-plaintext freeze records,
configuration/checkpoint/transform tampering, exact counters, resource caps,
and all 64 scoring assignments.

No real cache stat, hash, member, signal, or target value was read while
implementing or testing this milestone. No model was fit on real data, no real
prediction was created, and no validation score exists yet.

## Claim Boundary

Engineering capability added: NeuroDecodeKit now has a staged, bounded,
single-thread implementation for one hash-bound same-session S21 validation
event with isolated derivatives, causal CTC models, corruption controls,
prediction freezing, and one-shot scoring.

Scientific claim not established: synthetic implementation tests establish no
neural advantage, sensor-signal dependence, decoding accuracy, brain-specific
origin, source-test or cross-session behavior, unseen-person generalization,
real-time operation, EEG performance, portable/home use, or clinical utility.
