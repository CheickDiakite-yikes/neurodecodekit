# EEGMMIDB-UG1 Generated Qualification Closeout

Date: 2026-08-24

Status: **Stage G passed once; Stage M and every real-path operation remain closed**

Machine records:

- `registries/eegmmidb_unseen_participant_generalization_implementation.v0.json`
- `registries/eegmmidb_unseen_participant_generalization_stage_g_result.v0.json`

## Proof Order

The packet-bound authorization decision commit
`3e173f6dc61b1f6b32dcc9839aa74a67759b9b3f` passed CI `32694496933` before
Amendment 1. The narrowing amendment commit
`9ab8639b4d6fa28a30321687c82b185b13b1813a` then passed CI `32696449436`
before implementation.

The exact Stage G implementation commit
`da2be31a3ea4b7a438f86039c1d80b182e628ccf` passed Base Python job
`97363993816`, Optional Neuro Readers job `97363993465`, and CI
`32704970582`. Only after both jobs were green was the single generated/mock
qualification invoked.

## Capability Added

UG1 now has independent, bounded implementation surfaces for:

- exact 36-file acquisition planning and generated/mock transport;
- source/fresh participant, run, path, alias, and target firewalls;
- causal common-average reference, fixed SOS filtering, exact windows, and
  deterministic replay across chunks and run resets;
- the frozen shrinkage-LDA family and all 12 primary/control conditions;
- source-only feature normalization and participant-blind predictor inputs;
- canonical non-pickle checkpoints and target-free prediction commitments;
- isolated scoring with checkpoint rehashing before target delivery;
- atomic no-clobber publication and cumulative disk, output, wall-time, and
  process-tree RSS enforcement; and
- a sidecar CLI that leaves the historically hash-bound central CLI unchanged.

The sidecar command is:

```text
python -m neurodecodekit.eegmmidb_ug1_cli
```

`plan` is the no-network default. `qualify` is the consumed Stage G operation
and must not be invoked again for this registration.

## One-Shot Stage G Result

The one allowed generated/mock invocation passed all 17 registered adversarial
case classes. It exercised exact replay, target-swap/canary and participant
relabel invariance, split and filesystem refusals, future-impulse causality,
chunk replay, run reset, literal controls and views, canonical annotation
handling, completeness checks, checkpoint and prediction mutation refusal,
all router threshold boundaries, atomic crash behavior, resource failures, and
second-invocation refusal.

| Measure | Result |
|---|---:|
| Generated input bytes | 25,975,920 |
| Canonical public output bytes | 3,911 |
| Peak incremental output bytes | 1,450,304 |
| Runtime | 443.246267 seconds |
| Peak process-tree RSS | 276,856,832 bytes |
| Initial free disk | 99,378,757,632 bytes |
| Parameter-update fits | 61 |
| Participant-condition prediction sets | 420 |
| Model inference calls, including replay probes | 111 |
| Total model runs | 172 |
| Synthetic target deliveries / scoring events | 1 / 1 |
| Real path, cache, raw-data, or EDF reads | 0 |
| Real target deliveries | 0 |
| Network bytes / new payload bytes | 0 / 0 |

The canonical aggregate result was 3,911 bytes with SHA-256
`08bd7568c596c423825b799b2d4e1e67cf4066e2fd7ebd329eeb1a76ccc23359`.
It is recorded by hash and aggregate fields only; the temporary invocation
artifact is not part of the repository.

## Interpretation

The synthetic router reached `EEGMMIDBUG1-R4`, but that route has no scientific
meaning because every signal, target, participant, file, and prediction in the
qualification was generated. Its value is demonstrating that the strictest
success path, all controls, and all refusal paths are executable before any
real outcome can influence implementation choices.

The producer is causal under the frozen mechanical tests. End-to-end latency
was not measured. Visual-cue and ocular compatibility remain unresolved.

## Next Gate

Commit, push, and remotely green this closeout and its exact implementation and
result bindings. Stage M remains a separate Tier C metadata-only operation and
is not authorized by Stage G completion. No real EDF body, annotation, signal,
target, model result, or score may be accessed under this closeout.

Engineering capability added: UG1 now has a bounded, leakage-resistant,
causal, checkpointed, target-firewalled unseen-participant experiment pipeline
that passed its sole generated/mock qualification.

Scientific claim not established: no real EEG was opened or scored, so this
does not establish neural advantage, unseen-person generalization, movement
intention, motor-cortex origin, eye-independent information, language or
thought decoding, live decoding, or a hardware or clinical result.
