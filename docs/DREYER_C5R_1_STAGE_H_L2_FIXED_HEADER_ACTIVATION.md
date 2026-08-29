# DREYER-C5R-1 H-L2 Fixed-Header Activation

Date: 2026-08-29

Status: **no-authority activation record frozen; effective only after this
exact record is committed, pushed to GitHub `main`, and both required CI jobs
are remotely green**

Machine record:

- `registries/dreyer_c5r_1_stage_h_l2_fixed_header_activation.v0.json`

Activation ID: `DREYER-C5R-1-HL2-ACT0`

## Green Implementation Bound

The exact additive H-L2 implementation is commit
`a9cd0be7c22996154c28bb568e05c623606e7424`. GitHub Actions CI
`33260534900` passed Base Python job `99121591361` and Optional Neuro Readers
job `99121591482` on `main`. The activation binds six exact implementation,
CLI, test, and record artifacts totaling 79,741 bytes.

The generated-only qualification covered 32 transaction cases in 33 attempts,
including two byte-stable H1 replays and 31 refusal observations. It used zero
network bytes, zero real or private operations, and retained zero generated
payload bytes. Generated qualification is engineering evidence only.

## Activation Semantics

This record grants no authority by existing in a working tree or commit. It is
usable only when the executor is supplied the externally observed SHA-256 of
this exact machine record, the exact activation commit at `HEAD`, and the exact
positive CI run plus both required job IDs after that commit is remotely green.

Only then may the already authorized sole invocation consume itself by writing
the durable private marker before opener construction or request creation. The
invocation may make exactly one direct, proxy-free, verified-TLS GET and at
most one fixed-header semantic parse for:

```text
sourcedata/sub-01/eeg/sub-01_task-R1acquisition_eeg.edf
https://data.nemar.org/nm000250/v1.0.4/sourcedata/sub-01/eeg/sub-01_task-R1acquisition_eeg.edf
declared bytes: 14,805,604
SHA-256: a678fe6d37e0496eb381dcac6b877b047d02dfffc659ae4cfc38226f4850e185
```

The transaction has zero redirects, retries, ranges, resumes, substitutions,
or reruns. Success or failure consumes the sole attempt.

## Resource Envelope

```text
CPU threads / workers / numerical jobs:          1 / 1 / 0
runtime maximum:                                 300 seconds
peak process-tree RSS maximum:                   268,435,456 bytes
payload network maximum:                         16,777,216 bytes
incremental disk maximum:                        33,554,432 bytes
public output maximum:                           1,048,576 bytes
stream chunk maximum:                            1,048,576 bytes
free disk minimum before invocation:             10,737,418,240 bytes
real HTTP GETs / redirects / retries / reruns:   1 / 0 / 0 / 0
```

## Boundary At This Commit

This activation record performs no marker operation, request, download, real
or private path access, EDF open, header parse, annotation or sample read,
target delivery, model operation, score, stream, device action, release, or
claim upgrade. It neither accesses the remaining 119 EDFs nor activates a
larger acquisition.

Annotations, signal samples, events, trials, responses, task targets,
participant outcomes, models, predictions, scoring, and all scientific
interpretation remain forbidden in H-L2. A later successful H1 may establish
only the registered sensor-role roster, sampling rate, payload geometry, and
technical feasibility of the frozen Dreyer design.

Engineering capability added: one exact remotely green H-L2 adapter is now bound by a no-authority activation record that can unlock only a single bounded fixed-header transaction after its own remote-green proof.

Scientific claim not established: this activation performs no real EEG access and establishes no neural information, decoding, unseen-person generalization, peripheral-adjusted effect, live operation, hardware result, or clinical value.
