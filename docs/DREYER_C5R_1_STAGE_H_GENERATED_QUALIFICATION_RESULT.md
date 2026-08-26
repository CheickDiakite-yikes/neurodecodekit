# DREYER-C5R-1 Stage H Generated Qualification Result

Date: 2026-08-26

Status: **passed once; consumed; generated/mock engineering evidence only**

The sole registered qualification ran only after exact implementation commit
`634fc9826f16352abb4fa1fc940c7bc6c2a0a795` passed Base Python job
`98069988213`, Optional Neuro Readers job `98069988451`, and CI run
`32933431849`. The executor recollected that proof from fresh remote metadata
before creating any generated fixture.

## What Passed

The generated/mock run completed:

- two valid fixed-header streams using different chunk boundaries with exact
  payload and summary replay;
- 18 fail-closed cases covering HTTP status, redirect, missing/duplicate/wrong
  content length, transfer encoding, short/oversized/non-bytes bodies, digest
  drift, malformed EDF header, missing EEG, wrong EOG or EMG count, duplicate
  or unknown signal labels, wrong sampling rate, and no-clobber behavior;
- an exact generated roster of 27 EEG, three EOG, two EMG, and one annotation
  channel at 512 Hz for every physiological channel; and
- cleanup of invocation-created temporary files on every refusal.

The valid generated payload SHA-256 was
`c610db8334cc8c3db20455c428465c5ca1ec9cbdb175afa6f5c861620ceb6fe9`.
Its names are generated fixture values, not observations from the real Dreyer
file.

## Measurements

- runtime: 0.01751233299728483 seconds;
- peak process-tree RSS: 69,681,152 bytes;
- generated input: 194,048 bytes;
- private temporary payloads: 19,456 bytes;
- public result: 4,707 bytes;
- HTTP requests and network bytes: zero;
- payload hash passes and fixed-header parses on real data: zero;
- model, training, prediction, target-delivery, and score operations: zero;
- producer causal status: not applicable to a header preflight; and
- end-to-end latency: not measured.

The exact result is
`registries/dreyer_c5r_1_stage_h_generated_qualification_result.v0.json`,
4,707 bytes, SHA-256
`3472c0b8e391ea2464491cf2347aefcf62994726543f818a492d298babc4cd10`.

## Access Boundary

No real or private path was opened. No real HTTP request, network byte, EDF
payload byte, EDF header, annotation, signal sample, target, label, model,
training run, prediction set, target delivery, score, or claim upgrade
occurred. The only networked operations were one Git remote-metadata query and
two GitHub Actions metadata queries required for the proof barrier.

Stage H generated qualification is consumed and must not be rerun. The
committed result will make the registered output path no-clobber.

## Next Gate

The next gate is an all-false Tier C authorization packet for exactly one
direct GET of the pinned 14,805,604-byte `sub-01` R1 EDF. The future live
wrapper may be implemented only after that packet and authorization decision
are separately committed, pushed, and remotely green. The real operation must
park before the remaining 119 files on any transport, integrity, header,
sensor, or resource mismatch.

Engineering capability added: bounded stream verification, fixed-header
sensor-contract validation, deterministic replay, no-clobber publication, and
invocation-scoped cleanup passed the registered generated qualification.

Scientific claim not established: no real EEG information, unseen-person
generalization, EEG beyond peripheral signals, movement intention, language,
live decoding, hardware, or clinical result was tested.
