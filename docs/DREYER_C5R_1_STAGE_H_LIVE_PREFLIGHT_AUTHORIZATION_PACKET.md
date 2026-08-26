# DREYER-C5R-1 Stage H Live Preflight Authorization Packet

Date: 2026-08-26

Status: **request only; every authority flag remains false**

Machine request:

- `registries/dreyer_c5r_1_stage_h_live_preflight_authorization_request.v0.json`

Packet ID: `DREYER-C5R-1-HL`

## Why This Is The Next Gate

The independent Dreyer replication is now prospectively frozen and its full
target firewall, compact model, prediction freezer, and scorer have passed one
generated qualification. Stage H's streaming verifier has also passed one
registered generated/mock qualification with two valid replay cases and 18
adversarial refusals.

What remains unknown is small but decisive: whether one real source EDF
actually contains the preregistered 27 EEG channels, exactly three recorded
EOG channels, exactly two wrist EMG channels, and 512 Hz physiological samples.
If that assumption is wrong or ambiguous, acquiring the other 119 files would
waste roughly 1.76 GB and the strongest nuisance-controlled experiment would
not be executable as frozen.

This packet therefore asks to risk one exact 14,805,604-byte file and nothing
else. It grants no authority now.

## Immutable Proof Anchors

The Stage H implementation commit
`634fc9826f16352abb4fa1fc940c7bc6c2a0a795` passed Base Python job
`98069988213`, Optional Neuro Readers job `98069988451`, and CI
`32933431849` before the sole generated qualification.

The exact generated result commit
`af161844a9b49423a769440ed8f424bdae7836a0` passed Base Python job
`98071967562`, Optional Neuro Readers job `98071967693`, and CI
`32934121394`. The 4,707-byte result has SHA-256
`3472c0b8e391ea2464491cf2347aefcf62994726543f818a492d298babc4cd10`.
It reports zero real request, network byte, EDF byte, header read, signal read,
target read, model run, prediction, or score.

The machine request binds 16 exact research, contract, implementation, result,
and test artifacts totaling 151,485 bytes. Each byte count, SHA-256, Git path,
and the canonical artifact-set digest is frozen.

## Exact Real Member

Only this one public object is proposed:

- dataset: Dreyer et al. Dataset A, NEMAR `nm000250`, revision `v1.0.4`;
- path: `sourcedata/sub-01/eeg/sub-01_task-R1acquisition_eeg.edf`;
- direct URL: `https://data.nemar.org/nm000250/v1.0.4/sourcedata/sub-01/eeg/sub-01_task-R1acquisition_eeg.edf`;
- expected bytes: `14,805,604`; and
- expected SHA-256:
  `a678fe6d37e0496eb381dcac6b877b047d02dfffc659ae4cfc38226f4850e185`.

The other 119 R1/R2 EDFs, every R3-R6 file, sidecar, derivative, participant,
dataset, alternate host, redirect target, and substitute object remain closed.

## Requested Stage H-L1

Only after a separate authorization decision is committed, pushed, and both
required CI jobs are green, implement one additive standard-library live
wrapper around the already-qualified streaming verifier. Existing Stage G and
Stage H artifacts must remain byte-identical.

The wrapper must be qualified only with generated payloads and an injected
mock opener. It must:

- expose `plan` and generated `qualify` behavior before activation, with no
  usable live command until a separately green activation binds the exact
  implementation;
- create and sync a durable no-clobber consumed marker before constructing the
  real opener or making a request;
- prove from fresh remote metadata that the decision, implementation, and
  activation commits and both CI jobs are exact and green;
- use verified TLS, `Accept-Encoding: identity`, one direct GET, no redirect,
  retry, range, resume, credential, cookie, proxy substitution, or fallback;
- require exact status, final URL, one `Content-Length`, no encoding, exact
  body size, EOF, and SHA-256;
- stream through a unique Git-ignored temporary path in chunks no larger than
  1 MiB and atomically retain the complete payload only on H1 success;
- parse structurally only the fixed EDF header, never annotation records or
  signal samples;
- publish only the allowlisted aggregate sensor summary and resource ledger;
  and
- delete only temporary files created by that invocation on failure.

Generated qualification of the live wrapper is Tier B engineering work. It
must be committed, pushed, and remotely green before an activation can expose
the one real invocation.

## Requested Stage H-L2

Only after the exact live wrapper and activation are remotely green, one
irreversible invocation may:

1. confirm at least 10 GiB free disk without scanning another project;
2. write and sync the unique consumed marker;
3. make the one direct GET for the exact member above;
4. stream and SHA-256 verify exactly 14,805,604 body bytes;
5. parse only its fixed EDF header;
6. require the exact frozen 27-channel EEG roster, exactly three unambiguous
   EOG labels, exactly two unambiguous EMG labels, at most one recognized EDF
   annotation channel, no unknown/duplicate/blank label, and exactly 512 Hz on
   every physiological channel;
7. retain the complete private payload only if every gate passes; and
8. emit one aggregate public H1 or H0 result.

H1 permits only a future narrowing amendment that binds the observed EOG and
EMG names without changing their count or role. It does not authorize Stage A.
H0 permanently parks this Dreyer lane. Either outcome consumes H-L2; there is
no retry, rerun, repair, resume, substitution, or post-result amendment.

## Resource Envelope

| Resource | Frozen maximum or requirement |
|---|---:|
| CPU threads / workers / numerical jobs | 1 / 1 / 0 |
| Wall time | 300 seconds |
| Peak process-tree RSS | 256 MiB |
| Real HTTP GET requests | exactly 1 |
| Successful payload body bytes | exactly 14,805,604 |
| Payload-network cap | 16 MiB |
| Incremental disk peak | 32 MiB |
| Public output | 1 MiB |
| Stream chunk size | 1 MiB |
| Required free disk | 10 GiB |
| Redirects / retries / reruns | 0 / 0 / 0 |

TLS and transport-header byte counts unavailable to the standard library must
be reported as unavailable. The enforceable network count is the exact body
byte ledger plus one request and zero redirect/retry.

## Explicit Exclusions

This request does not authorize any implementation, generated qualification,
activation, network request, real path access, payload byte, or header read
now. Its proposed maximum also excludes:

- the remaining 119 R1/R2 files, R3-R6, any sidecar, companion, alternate
  participant, file, dataset, download, redirect, retry, or substitution;
- reading or publishing EDF patient, recording, date, raw-header, annotation,
  event, trial, task, target, label, signal-sample, quality, reference,
  geometry, or individual outcome values;
- creating a split, epoch, window, feature, cache, derivative, checkpoint,
  model input, prediction, or target envelope;
- model access, parameter update, training, inference, calibration, selection,
  prediction freeze, target delivery, or scoring;
- inspecting, modifying, moving, deleting, reopening, or publishing any
  consumed BNCI, EEGMMIDB, S20, S21, S24, S25, SpanishBCBL, or other private
  payload or artifact;
- language models or providers, RW3, streams, devices, hardware, upload,
  release, publication, or another project; and
- any scientific, neural, decoding, unseen-person, motor-intention,
  motor-cortex, eye-independent, language, live, portable, home-use,
  assistive, or clinical claim upgrade.

## Decision Boundary

Every authority flag in the machine request is false. This request and a
separate proof-only closeout must first be committed, pushed, and remotely
green. Only then may `DREYER-C5R-1-HL` be named as the sole active Tier C
packet. The maintainer's next unambiguous packet-bound `approve`, `continue`,
or `proceed` may authorize only the exact H-L1 then H-L2 sequence above under
the research-autonomy charter.

Engineering capability requested: add a proof-bound one-file live wrapper and
use it once to verify the exact payload and sensor-header assumptions before
any bulk cohort acquisition.

Scientific claim not established: this all-false request performs no real
data operation and establishes no EEG effect, unseen-person generalization,
EEG beyond peripheral controls, movement intention, language decoding, live
performance, hardware result, or clinical utility.
