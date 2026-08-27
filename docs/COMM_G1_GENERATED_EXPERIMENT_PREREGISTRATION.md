# COMM-G1 Generated Experiment Preregistration

Date: 2026-08-27

Status: **Prospectively frozen Tier A contract. Generated implementation may
begin only after this exact registration is remotely green. The one generated
qualification may run only after that exact implementation is remotely green.
Every real-data, target, model-evidence, stream, device, and claim authority is
false.**

Contract: `registries/comm_g1_generated_experiment_contract.v0.json`

## Objective

Qualify the complete communication-experiment control plane on generated data:

```text
generated multichannel rows
  -> strict reader and role validation
  -> forward-only preprocessing
  -> participant-isolated residualization and compact models
  -> target-blind held-out predictions
  -> aggregate hash-only prediction freeze
  -> one synthetic target delivery and one synthetic score
```

The qualification must prove that the pipeline can distinguish a generated
EEG increment from eye, mouth, posterior, cue, timing, and no-signal shortcuts.
It must also prove that each shortcut-only fixture is routed away from an
EEG-specific pass.

This is generated engineering. It does not inspect or imitate a real BDF,
assume that real `ds003626` metadata has passed, or estimate a scientific
effect.

## Parent Evidence

The communication claim program is remotely green. COMM-L0's generated
source-identity implementation and result are consumed, and its proof-only
closeout is remotely green. The 2026-08-27 replication-source refresh is also
remotely green and confirms that no independent full-control cohort is
operationally qualified.

These are control-plane prerequisites, not scientific prerequisites. Real
OpenNeuro metadata, channel semantics, events, payload identity, and trial
structure remain unverified and unauthorized.

## Generated Cohort

Use six fictional participants, three sessions per participant, four command
classes, and two repeats per class and session: 24 rows per participant and
144 rows total. Every outer fold holds out exactly one participant with zero
signal fitting, target fitting, calibration, threshold selection, or
adaptation rows from that person.

Each row contains generated arrays only:

- eight EEG channels: four central, two posterior, and two frontal;
- four EOG channels;
- two bilateral oral-EMG channels;
- cue and timing fields;
- source indices and timestamps; and
- one synthetic class code kept outside every held-out fold capability until
  the synthetic prediction freeze is complete.

Use 128 Hz generated sampling and one-second, 128-sample left-context windows.
The generated decision point is 1.5 seconds after a known fixture onset. The
known onset is permitted only for this offline engineering qualification and
cannot count as source-only endpointing or live decoding.

The fixture generator may inject class-dependent structure into selected
generated channels to test positive and negative routes. It may not include
words, reference text, intended text, participant metadata, copied source
samples, real channel labels, or any real dataset response.

## Causal Preprocessing

All transforms are forward-only and operate on samples at or before the
decision time. Use fixed per-channel log relative band power in 4-8, 8-13,
13-20, and 20-30 Hz, normalized by 2-40 Hz power with a periodic Hann window
and fixed epsilon. The generated implementation must emit availability times,
true lengths, masks, channel roles, source rate, and required context.

Source-participant standardization, nuisance residualization, and every fitted
state are learned inside the outer fold. Missing, duplicated, reordered, or
cross-participant rows refuse; no interpolation, ICA, channel deletion,
target-derived rejection, row-random split, or held-out normalization is
allowed.

## Fixed Controls And Models

For each outer fold, fit one source-only ridge residualizer that predicts the
central EEG feature vector from EOG, oral EMG, posterior EEG, cue, and timing.
Freeze alpha `10.0` with source-only standardization.

Every trainable classification arm uses the same source-scaled multinomial L2
logistic family: `C=0.1`, `lbfgs`, `max_iter=1000`, `tol=1e-6`, no class
weights, fixed probability clipping, one CPU thread, and no hyperparameter
selection. Nonconvergence parks the qualification.

The ten arms are:

1. equal prior;
2. source class prior;
3. cue plus timing;
4. EOG only;
5. oral EMG only;
6. all peripheral/context controls `P`;
7. selected EEG only;
8. posterior EEG only;
9. `P + residual EEG`; and
10. `P + participant-and-session-matched deranged residual EEG`.

Derangement is a deterministic adjacent-pair swap within each source
participant, session, and class, with no wraparound. It preserves dimension,
row count, and marginal scale while breaking the row-level EEG relationship.

The generated schedule is exact: six outer folds, six residualizer fits, 54
classifier or prior fits, 60 inference/prediction sets, 1,440 prediction rows,
one aggregate hash-only prediction freeze, one synthetic target delivery, one
synthetic score, zero post-target update, and zero rerun.

## Positive And Negative Routes

The generated positive fixture routes to `COMM-G1-R1` only when `P + residual
EEG` improves held-out participant-macro log loss over both `P` and `P +
deranged residual EEG` by at least 0.10 and all six participants have positive
margins. This threshold validates generated routing only.

The EOG-only, oral-EMG-only, posterior-only, cue-only, timing-only, no-signal,
and mixed-without-increment fixtures must not reach `R1`. Their expected routes
identify the shortcut that explains the synthetic predictions. A target-leak,
participant-collision, split-leak, malformed-role, prediction-tamper,
pre-freeze target-delivery, or resource violation routes to `COMM-G1-R0`
without an accepted score.

No generated route has scientific value. A generated `R1` means only that a
known injected residual EEG effect survives the exact synthetic controls.

## Target Firewall And Freeze

Each fold capability may access only five source participants' signal and
synthetic targets plus one held-out participant's signal. It cannot enumerate,
open, infer, or traverse another fold, the held-out target envelope, or the
scoring key.

The public prediction freeze contains only schema, condition identities,
counts, dimensions, configuration hashes, aggregate prediction hashes, and
warnings. It contains no individual prediction, probability, target,
participant outcome, row path, or capability path.

The scorer accepts the same 144 synthetic targets once only after the freeze
hash is sealed in the generated work directory. It refuses missing, repeated,
reordered, extra, or mismatched rows and records zero updates after delivery.

## Qualification Matrix

The implementation must generate and qualify:

- two byte-identical clean replays in separate work directories;
- one positive residual-EEG fixture;
- seven shortcut-only fixtures;
- participant, session, split, capability, row-order, role, channel, mask,
  timestamp, geometry, and sampling-rate adversaries;
- source-only state, residualizer, derangement, prediction-freeze, target
  envelope, scorer, no-clobber, symlink, resource, and determinism adversaries;
  and
- at least 30 independently reachable refusal IDs.

The generated implementation may expose only `plan`, `qualify`, and aggregate
`inspect`. It may not expose a real dataset path, URL, request, download,
execute, training, scoring, stream, device, or provider mode.

## Resources And Authority

```text
CPU threads / workers / numerical jobs:  1 / 1 / 1
generated qualification invocations:     1 after green implementation
wall time:                                180 seconds
peak process-tree RSS:                    536,870,912 bytes
generated input bytes:                    33,554,432 maximum
private generated bytes:                  33,554,432 maximum
public output bytes:                      1,048,576 maximum
network / provider bytes:                 0
real or private dataset bytes:            0
incremental real payload bytes:           0
real target deliveries / scores:          0 / 0
stream / device operations:               0 / 0
reruns:                                    0
```

The 20 GiB total research-storage ceiling and 10 GiB selected-raw ceiling are
unchanged. Generated work must remain below 32 MiB and clean only temporary
files created by its own invocation. It may not inspect, modify, move, or
delete ignored research state, the unrelated tracker inspection file, or any
other project.

After this exact registration is committed, pushed, and both required CI jobs
pass, Tier B may implement the generated-only pipeline. The sole official
qualification may run only after that exact implementation is committed,
pushed, and remotely green. Real metadata, payload, signal, target, model,
prediction, score, provider, stream, device, release, and claim operations
remain separate Tier C gates.

`DREYER-C5R-1-HL` remains the sole active Tier C packet, with every authority
flag false.

## Claim Boundary

Engineering capability proposed: a deterministic generated experiment can
prove the reader, causal controls, participant firewall, compact schedule,
prediction freeze, and isolated scorer behave correctly before real data.

Scientific claim not established: this registration and any generated pass
cannot establish communication or inner-speech decoding, EEG beyond eye or
mouth activity, unseen-person generalization, independent replication, live
decoding, hardware performance, unrestricted thought reading, or clinical
value.
