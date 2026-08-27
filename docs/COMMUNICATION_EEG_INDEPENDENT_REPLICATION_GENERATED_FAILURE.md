# COMM-R0-G Generated Qualification Failure

Date: 2026-08-27

Status: **Failed closed; consumed and permanently parked**

Machine record:
`registries/communication_eeg_independent_replication_generated_failure.v0.json`

## Ordered Proof

The official generated qualification did not begin until activation
`9b47f15` and final activation proof `0071843` had each been pushed and had
passed both required CI jobs. Execution HEAD was exactly `0071843`; the
qualified executor SHA-256 was
`032dc10eccb35eebf02126cec0b7e2a539a294e737e448b83d5beca775e32aa8`.

Before execution, the registered result did not exist, Git had no tracked
worktree change, approximately 50 GiB was free, and the unrelated tracker
inspection file was left untouched. The invocation used one CPU thread, one
worker, one numerical job, generated fictional arrays only, and zero network.

## Result

The sole invocation ran both generated child replays and returned the required
adversarial refusal sequence. The adversarial `symlink_escape` case correctly
created a symlink inside its isolated test directory and confirmed that
publication through it was refused. That expected fixture was not removed.

The next step audited the entire temporary tree and rejected every symlink.
It therefore encountered the retained adversarial fixture and raised
`G2-TEMPORARY-SYMLINK` before assembling or publishing the registered result.
This was an internal qualification-ordering defect, not evidence of an
external filesystem escape or unexpected symlink.

The `finally` cleanup removed the invocation directory. No generated
prediction, target, or score artifact remains, and the registered result path
is absent. No retry or rerun was attempted. The one-shot invocation is
consumed and may not be rerun.

## Accounting

Program control flow reached the post-adversarial tree measurement only after
two child replays returned. The frozen schedule therefore executed 312
generated parameter-update fits, 288 generated inference runs, 360 generated
prediction sets, 8,640 generated prediction rows, two synthetic target
deliveries, and two synthetic scores. None is accepted as an official result,
and all have zero scientific value.

The launcher observed approximately 5.0 seconds wall time. Exact executor
runtime, peak process-tree RSS, generated input bytes, private generated
output bytes, and temporary disk bytes are unavailable because the exception
preceded result assembly. Those unavailable values are recorded as `null`,
not fabricated as zero. Public result bytes were zero.

Every real-path, raw-data, cache, signal, target, label, model, training,
prediction, delivery, score, network, provider, stream, device, hardware,
release, and scientific-claim counter remained zero. Producer causality is
unavailable because no official result was accepted, and end-to-end latency
was not measured.

Failure record `9876cf9` passed Base Python job `98606113010`, Optional Neuro
Readers job `98606113427`, and CI `33097495998`. This remote proof records the
failed invocation; it does not turn the rejected synthetic work into an
accepted result or authorize a rerun.

## Next Gate

`COMM-R0-G` is permanently parked. A narrow source correction may remove the
adversarial fixture before final tree measurement, but the corrected executor
can run only under a new prospective generated qualification gate. It cannot
retroactively validate this invocation.

The sole active Tier C gate remains `DREYER-C5R-1-HL`, with every authority
flag false. This generated failure does not authorize a Dreyer request, real
EEG access, model execution, target delivery, scoring, release, or claim
upgrade.

## Claim Boundary

Engineering capability added: the activated generated executor failed closed
on an internally retained symlink fixture and cleaned all invocation-created
temporary state without publishing a misleading result.

Scientific claim not established: No real EEG was accessed and no
communication decoding, unseen-person generalization, EEG-beyond-controls,
live, hardware, or clinical result was established.
