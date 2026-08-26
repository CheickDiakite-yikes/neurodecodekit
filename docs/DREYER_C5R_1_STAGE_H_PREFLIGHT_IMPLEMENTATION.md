# DREYER-C5R-1 Stage H Preflight Implementation

Date: 2026-08-26

Status: **Generated/mock implementation only. No real request, payload, EDF
header, annotation, signal, target, model, prediction, or score is authorized.**

## Why Stage H Exists

The Dreyer replication depends on three recorded EOG channels, two wrist EMG
channels, the frozen 27-channel EEG roster, and an exact 512 Hz physiological
sampling rate. The public paper and manifest support that design, but a
payload-level header check has not occurred. Downloading all 120 source EDFs
before checking that assumption would spend roughly 1.78 GB and could leave us
with an unusable nuisance-control design.

Stage H therefore risks exactly one pinned 14,805,604-byte `sub-01` R1 file.
If its fixed header is absent, ambiguous, or different, the lane parks before
the other 119 files.

## Implemented Surface

The standard-library verifier accepts an already-open response and:

1. requires status 200 and the exact final HTTPS URL;
2. requires exactly one matching `Content-Length` and no `Content-Encoding`;
3. writes through a no-clobber temporary file while computing SHA-256;
4. reads and parses only the fixed EDF header as structured content;
5. checks the exact 27 EEG labels, exactly three EOG labels, exactly two EMG
   labels, at most one recognized EDF annotation channel, no unknown or
   duplicate label, and 512 Hz on every physiological channel;
6. streams the remaining body opaquely without annotation or signal parsing;
7. requires exact byte count, EOF, SHA-256, regular-file identity, and size;
8. promotes the complete payload only after every gate passes; and
9. removes only its own temporary file on failure.

The allowlisted sensor summary excludes EDF patient, recording, date, raw
header, annotation, event, trial, target, label, and signal values. Exact EOG
and EMG labels may be recorded because the preregistration requires a later
narrowing amendment to bind those nuisance channels without changing their
roles or counts.

## Generated Qualification

The sidecar CLI exposes only `plan`, `qualify`, and `inspect`. It has no live
request or execute command. One registered generated qualification may run
only after this exact implementation commit is pushed and both required CI
jobs are green.

The generated suite covers valid replay plus status, redirect, header
multiplicity, transfer encoding, short/long/non-bytes body, digest, fixed-header,
EEG/EOG/EMG roster, duplicate/unknown label, sampling-rate, no-clobber, and
failure-cleanup cases. It uses no NumPy, MNE, scikit-learn, or other new base
dependency.

## Proposed Real Envelope

A later exact Tier C decision may authorize one direct, no-retry GET for only:

- URL: `https://data.nemar.org/nm000250/v1.0.4/sourcedata/sub-01/eeg/sub-01_task-R1acquisition_eeg.edf`;
- bytes: `14,805,604`; and
- SHA-256: `a678fe6d37e0496eb381dcac6b877b047d02dfffc659ae4cfc38226f4850e185`.

That proposed invocation is capped at one CPU thread, one worker, 300 seconds,
256 MiB peak process-tree RSS, 16 MiB network payload, 32 MiB incremental disk,
1 MiB public output, and at least 10 GiB free disk. It permits one opaque hash
pass and one fixed-header parse, and nothing else.

## Stop Rule

`DREYERC5R-H1` means only that the exact file and sensor header contract passed.
The observed EOG/EMG names must then be bound in a narrowing amendment before
Stage A. `DREYERC5R-H0` permanently parks this lane. There is no retry,
substitution, redirect, partial success, or fallback dataset.

Engineering capability added: a bounded stream, integrity verifier, strict
EDF fixed-header sensor-contract check, no-clobber publisher, and
invocation-scoped cleanup path now exist for generated qualification.

Scientific claim not established: no real EEG information, unseen-person
generalization, EEG beyond peripheral signals, movement intention, language,
live decoding, hardware, or clinical result has been tested.
