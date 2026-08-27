# COMM-L0 Generated Source Identity Qualification Result

Date: 2026-08-27

Status: **passed once; consumed; generated engineering evidence only**

The sole registered qualification ran only after implementation commit
`be6c44fcfd7363bf0c0899bc1b737e588070c760` passed Base Python job
`98405103426`, Optional Neuro Readers job `98405103509`, and CI run
`33038044421`.

## What Passed

The generated-only run completed:

- two deterministic replays whose synthetic file rows arrived in opposite
  source orders but produced the same canonical tree and selection summaries;
- all 20 registered adversarial refusals, including snapshot, DOI, GraphQL,
  JSON, path, participant, session, raw-file, derivative, and storage-cap
  violations;
- exact retention of ten generated participants, one common complete session
  per participant, ten generated BDF identities, and 30 generated companion
  identities; and
- aggregate-only publication with no path, URL, version ID, row record,
  participant outcome, event, target, or label.

The selected generated fixture summarized 40 objects and 1,029,510 bytes. The
complete generated tree summarized 121 objects and 3,089,072 bytes. These are
synthetic test values, not observations about the OpenNeuro dataset.

## Measurements

- runtime: 0.07287466689012945 seconds;
- peak RSS: 22,069,248 bytes;
- generated input: 39,137 bytes;
- generated aggregate output: 3,001 bytes;
- CPU threads, workers, and numerical jobs: one each;
- network and real payload bytes: zero;
- dataset-specific requests and real/private reads: zero;
- BDF headers, signal samples, events, targets, and labels: zero;
- model runs, predictions, scores, and claim upgrades: zero;
- producer causal status: not applicable to metadata identity; and
- end-to-end latency: not measured.

The exact committed result is
`registries/communication_eeg_source_identity_generated_qualification_result.v0.json`,
3,001 bytes, SHA-256
`39b0833ac821246a7159fda7575f6cfa3c1f621fd3acb64af6f3fa07fe3fb48d`.

## Safety Boundary

This qualification used generated fixture bytes only. It did not query
OpenNeuro, read a dataset-specific response, request or download a payload,
open a real or private path, or inspect any BDF header, event, target, label,
or signal sample. It did not train, infer, freeze a prediction, score, stream,
operate a device, publish a release, or upgrade a scientific claim.

The qualification is consumed and must not be rerun. The ignored execution
result remains isolated; the committed aggregate ledger is byte-identical.
The unrelated untracked tracker inspection file remains untouched.

## Next Gate

COMM-L0 engineering is qualified, but real source identity is still
unverified. A future dataset-specific metadata operation requires its own
all-false Tier C request, proof, and exact maintainer decision. It cannot
silently displace `DREYER-C5R-1-HL`, which remains the sole active Tier C
packet, and it cannot request a payload.

Engineering capability added: the strict all-person source canonicalizer and
bounded raw-session selector passed deterministic replay and every registered
generated refusal under its resource and privacy caps.

Scientific claim not established: no real EEG, communication decoding,
unseen-person generalization, EEG-beyond-eye-or-mouth effect, replication,
live operation, hardware performance, or clinical value was tested.
