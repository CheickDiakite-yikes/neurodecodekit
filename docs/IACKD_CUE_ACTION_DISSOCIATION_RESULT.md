# IACKD Cue-to-Action Reversal Result

Date: 2026-08-10

Status: **Acquisition passed; analysis consumed and parked at `IACKD-F10`
before signal samples, targets, fitting, inference, or scoring; no rerun**

Registry:
`registries/iackd_cue_action_dissociation_result.v0.json`

## Ordered Gate Proof

Exact implementation `f5c36baffefc3889c006a515d06bc42cd2b5cb78` was pushed
before any real IACKD operation. CI run `31409141349` passed Base Python job
`93522699446` and Optional Neuro Readers job `93522699599` on that exact
commit. The tracked worktree was clean, all registered output roots were
absent, and 49,317,097,472 bytes were free before acquisition.

## Acquisition Result

The single no-retry acquisition passed every registered gate.

| Measure | Observed |
|---|---:|
| Metadata requests | 4 |
| Listed objects | 1,679 |
| Listed bytes | 7,966,799,433 |
| Selected objects | 1,340 |
| Selected payload bytes | 7,249,113,684 |
| Sequential payload requests | 1,340 |
| Streaming SHA-256 passes | 1,340 |
| Payload content parses | 0 |
| Post-write content opens | 0 |
| Runtime | 679.749484 seconds |
| Peak RSS | 126,205,952 bytes |
| Peak incremental disk upper bound | 7,249,694,270 bytes |
| Free disk after promotion | 41,882,632,192 bytes |
| Retries / reruns | 0 / 0 |

The canonical inventory SHA-256 was
`c30b518f9dafe3d46128849725e1f2f8fdce33239fbf6ade8603d66a64f0ffa5`.
The private 580,128-byte acquisition manifest has SHA-256
`99dcdf587cba202422e25b92082ff90add8512a2769902f59aab67dee52334e2`.
The 261-byte private human receipt has SHA-256
`507dd4d7c3b2414df3473aef63d18975d16dffb530f61972c38008487ffb4f3a`.
Neither artifact is committed because it belongs to the Git-ignored private
acquisition root.

The complete acquired bundle remains isolated and retained. It was not
deleted, moved, renamed, uploaded, or published.

## Consumed Analysis Failure

The one registered analysis invocation wrote its 144-byte no-rerun consumed
marker before bundle inspection. It then:

1. verified exact bundle membership;
2. read and validated the private acquisition manifest;
3. completed one new sequential size and SHA-256 pass over all 1,340 objects;
4. invoked MNE `1.12.1` on the first deterministic BrainVision run; and
5. stopped at the frozen channel-inventory gate with the exact public error
   `BrainVision channel inventory is not 32+4`.

This is registered refusal `IACKD-F10-channel_sampling_or_geometry_failure`.
The check requires exactly 36 BrainVision channels and the normalized presence
of M1, M2, HEOG, and VEOG. The error does not distinguish whether the observed
count differed from 36, one or more required names used an unregistered alias,
or both. The observed channel list and count were not logged or retained, so
they are unavailable and are not invented here.

MNE may resolve linked BrainVision companions while constructing a lazy reader;
therefore this closeout conservatively records one header parse and up to one
linked marker-companion parse. The failing check occurs before `raw.get_data()`
and before NeuroDecodeKit reads the channels TSV, EEG sidecar, geometry,
events TSV, ball stream, Leap stream, signed displacement, or any target.

The process-level wall time was 21.443608 seconds, including one temporary
Matplotlib font-cache build. Peak RSS for the failed analysis was not retained
because the exception occurred before the structured analysis receipt; it is
reported as unavailable rather than inferred. The registered 2 GiB cap was
checked throughout the complete object-hash pass, and no resource-cap error was
emitted.

## What Remained Closed

The execution produced no fit derivative, target-free final derivative, sealed
target artifact, private prediction payload, physiology summary, or public
prediction freeze. Consequently:

- signal sample materializations were zero;
- channels-TSV, geometry, event, ball, and Leap parses were zero;
- final target or label rows delivered to any model were zero;
- parameter-update fits and model-inference calls were zero;
- prediction sets and prediction freezes were zero;
- final-target deliveries and scoring events were zero; and
- post-target updates, retries, and reruns were zero.

No `IACKD-R0` through `IACKD-R4` scientific route applies because the
experiment stopped before prediction. This is an integrity-gate result, not a
null neural result.

## Disposition

IACKD-1 is consumed and parked with no retry, rerun, parser relaxation, alias
substitution, or post-failure local inspection authorized. The acquired public
bundle may support a future separately preregistered, metadata-minimal channel
inventory audit, but this result does not authorize reopening it. A new design
must learn the actual declared inventory without exposing signal samples,
targets, trajectories, or participant outcomes, then freeze any corrected
reader contract before another evidence-bearing run.

Engineering capability added: NeuroDecodeKit acquired and opaque-verified the
exact 7.249 GB IACKD source under strict resource limits and demonstrated that
the target-blind analysis fails closed at a preregistered channel contract
instead of silently deleting, relabeling, or adapting channels.

Scientific claim not established: no signal sample, target, model prediction,
or score was produced, so this result establishes no EEG effect, action or cue
alignment, brain-specific origin, generalization, typing, language or thought
decoding, real-time operation, hardware capability, assistive benefit, or
clinical use.
