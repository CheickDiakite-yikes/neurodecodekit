# Loop 48 Stage B Train-Only Failure-Discrimination Authorization Packet

Date: 2026-07-15

Status: **Awaiting the exact user authorization sentence**

Current execution state: **Unauthorized; every `authorized_now` field is false**

Green preregistration commit: `0ee0ab7cd3abae4ce654af9954854a6e236c8a0e`

Green push CI: [run 29452286159](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/29452286159)

Green PR CI: [run 29452288520](https://github.com/CheickDiakite-yikes/neurodecodekit/actions/runs/29452288520)

Machine request: `registries/loop48_stage_b_authorization_request.v0.json`

Registered contract:
`registries/loop48_train_only_discrimination_contract.v0.json`

## Decision In Plain English

This is permission to implement and execute one small diagnostic experiment
inside the existing S21 session-1 **source-train** partition. It is designed to
tell us why the exact Loop 26 model failed before we spend storage on a new
participant or enlarge the model.

If separately authorized, NeuroDecodeKit may:

- verify one exact 10,632,576-byte sentence-cache identity;
- read target-free split metadata and stream only the registered source-train
  rows into isolated derivatives;
- fit exactly 20 tiny models, run exactly 35 target-blind inferences, fit five
  no-signal priors, and freeze exactly 41 prediction sets;
- keep 11 check targets away from every fit, prediction, threshold, and stop
  decision until a hash-only prediction record is committed, pushed, and
  remotely green; and
- deliver and score those same 11 check targets once, emit all six hypothesis
  outcomes together, and stop without tuning or rerunning.

No outcome is predicted. A positive result and a negative result are both
useful diagnostic evidence when retained under the same frozen rules.

## Why This Is Worth Doing Before New Acquisition

Loop 48 Stage A showed a `99.3477%` blank-dominant primary output and strong
seed dispersion, but aggregate artifacts could not identify the cause. Stage B
uses one shared evidence bundle to test:

1. exact tiny-CTC optimization feasibility;
2. gross transformed-cache quality defects;
3. timing sensitivity;
4. separability under the registered candidate and linear probes;
5. no-signal prior dominance; and
6. bounded data quantity or sentence-diversity effects.

The source cache is about 10.6 MB and the complete budget remains one CPU
thread, under 1 GiB RSS, and under 32 MiB of generated output. Loop 49 still
remains necessary for fresh-person development evidence.

## Historical-Use Correction

All 55 source-train rows contributed to earlier Loop 26 fits. The deterministic
44-fit/11-check split prevents leakage **inside this new execution**, but the 11
rows are not historically unseen and cannot become an independent test.

The maximum possible result is therefore **E2 pipeline-discriminative
evidence**, not E3 sensor-dependence confirmation, independent validation, or
neural advantage.

## Exact Input Boundary

| Input | Frozen value |
|---|---|
| Sentence cache | `cache/loop14_s21_split_aware/base_102mag_100hz_trainfit.npz` |
| Cache bytes | `10,632,576` |
| Cache SHA-256 | `45ad465bb2512d827a6d8863b05ddd269c950701cc09535aa086120839d56815` |
| Cache shape | `66 x 102 x 617`, float32, 100 Hz |
| Split report | `cache/loop14_s21_split_aware/split/split.json` |
| Split report SHA-256 | `cd0001b49666352919ea137859a6948a5e96c467def2e2b9c08be8c1c94574ef` |
| Eligible source rows | 55 source-train rows only |
| New diagnostic split | 44 fit / 11 target-withheld check |

Validation, source test, session 2, S7, S20, S25, raw FIF/MAT, private Loop 26
checkpoints, and private Loop 26 predictions remain closed.

The source is a monolithic deflated NPZ. Opaque traversal of excluded members
may occur while the bounded reader returns only registered rows. The result may
not claim physical nonaccess; it must report the exact delivery counters.

## Exact Operation Inventory

| Operation | Exact amount |
|---|---:|
| Source-cache SHA-256 passes | 1 |
| Fit signal/target rows | 44 / 44 |
| Pre-freeze check signal/target rows | 11 / 0 |
| Parameter-update runs / optimizer steps | 20 / 4,800 |
| Target-blind model-inference runs | 35 |
| Train-only no-signal prior fits | 5 |
| Frozen prediction sets | 41 |
| Post-green-freeze check targets | 11, delivered once |
| Check scoring events | 1 |
| Validation, source-test, or session-2 rows | 0 |
| Downloads | 0 bytes |
| Reruns after check scoring | 0 |

Models remain the exact 2,908-parameter causal candidate and 2,884-parameter
linear comparator. Seeds are exactly `4801`, `4802`, and `4803`; there is no
favorable-seed selection, early stopping, restart, larger model, or additional
architecture.

## Controls And Statistical Gate

The frozen evidence bundle includes:

- a size-matched train-only prior;
- exact-zero signal;
- whole-row prediction derangement;
- fixed-point-free channel derangement;
- four nonwrapping fine shifts at `-50, -25, +25, +50` samples;
- one severe `+100` sample shift;
- one timing-only fit; and
- one fit-target derangement fit.

Every check comparison uses sentence-level CER differences and all
`2^11 = 2,048` exact paired sign assignments. The primary candidate must beat
each of seven registered comparators by at least `0.05` macro sentence CER with
one-sided exact `p <= 0.05`; every component is required. Fine shifts use the
frozen Bonferroni threshold `p <= 0.0125`.

The candidate/linear separability rule is separate: all three candidate and
all three linear size-44 sets compare with the same prior. It does not pretend
that linear corruption predictions or a task-locked character probe exist.

## Computer And Storage Envelope

| Resource | Hard cap |
|---|---:|
| CPU threads / workers / concurrent jobs | 1 / 1 / 1 |
| Parameter-update runtime | 600 seconds total |
| End-to-end runtime | 900 seconds total |
| Peak RSS | 1 GiB |
| Working arrays | 128 MiB |
| Checkpoints | 4 MiB total |
| Private predictions | 4 MiB total |
| All generated artifacts | 32 MiB total |
| Required free disk before execution | 20 GiB |
| New data or model downloads | 0 bytes |

The last measured free space was 39 GiB. Loop 26 completed a similar 21-fit
event in 184.05 seconds at 522,797,056 bytes peak RSS and 10,126,825 generated
bytes. These observations justify headroom; they are not a performance
guarantee. Any cap, hash, identity, count, or nonfinite-value failure parks the
stage without cleanup or retry authority.

## Required Order

1. Record the exact sentence below in a separate authorization-only registry.
2. Test, commit, push, and obtain green CI for that authorization record.
3. Implement the bounded reader orchestration, isolation, training, controls,
   freeze writer, scorer, and synthetic-only tests without protected access.
4. Test, commit, push, and obtain green CI for that implementation.
5. Bind identities, environment, resources, and 44/11 membership without
   signal or target delivery.
6. Perform one cache SHA-256 pass and create 44-row fit plus 11-row target-free
   check-input derivatives.
7. Run the static audit, 20 fits, 35 target-blind inferences, five priors, and
   freeze 41 prediction sets.
8. Commit and push one plaintext-free prediction-freeze record and obtain green
   CI.
9. Deliver the same 11 check targets to one isolated scorer once.
10. Emit every hypothesis, control, curve, warning, resource, and unavailable
    field together, mark this check partition consumed for the protocol, and
    stop without tuning or rerunning.

## Exact Authorization Sentence

To authorize this exact scope, send the following sentence verbatim:

```text
Authorize the Loop 48 Stage B train-only failure-discrimination implementation and one registered execution exactly as scoped in docs/LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md and registries/loop48_train_only_discrimination_contract.v0.json. I authorize one SHA-256 pass over the named 10,632,576-byte S21 session-1 sentence cache; target-free reading of the bound split metadata; opaque sequential traversal of its deflated members; delivery of exactly 44 source-train signal/target rows and 11 source-train check signal rows into isolated derivatives; 20 bounded parameter-update runs, 35 target-blind model-inference runs, five train-only no-signal prior fits, 41 frozen prediction sets, and one conditional delivery and scoring of the same 11 source-train check targets only after the hash-only prediction-freeze record is committed, pushed, and remotely green. I authorize no validation or source-test row delivery or scoring, session 2, S7/S20/S25, raw FIF/MAT reads, new downloads, larger or additional models, restarts, language models, NeuroTokens, RW3, streams, devices, hardware, post-check tuning, claim upgrade beyond the registered E2 diagnostic ceiling, or rerun after check scoring.
```

General continuation, co-researcher status, the draft autonomy charter, and the
consumed Stage A or Loop 26 authorizations do not substitute for this sentence.
The request remains immutable and unauthorized after it is green; a separate
decision record must capture the sentence if it is supplied.

## Maximum Possible Result

A clean Stage B can establish only whether, under this one frozen post-outcome
diagnostic, intact transformed source-train sensor input did or did not
outperform the specified signal-free and corrupted comparators on 11 rows
excluded from these new fits.

## Still Not Established After A Pass

A pass cannot establish independent validation, neural advantage,
brain-specific origin, useful decoding, unseen-person generalization, causal
preprocessing, end-to-end or real-time latency, EEG or portable/home-device
performance, assistive value, diagnostic value, or clinical utility.

## Current Proof Boundary

The preregistration commit and both CI runs are green. No Stage B
implementation, cache stat or hash, member read, isolated derivative, model
operation, training operation, prediction freeze, check-target delivery,
scoring event, generated experiment artifact, or scientific result exists.
